from typing import Type

import requests
from bs4 import BeautifulSoup
from fake_useragent import UserAgent
from html2text import html2text
from langchain.callbacks.manager import CallbackManagerForToolRun
from langchain.chains import RetrievalQA, create_qa_with_structure_chain
from langchain.chains.combine_documents.stuff import StuffDocumentsChain
from langchain.docstore.document import Document
from langchain.document_loaders import PyMuPDFLoader
from langchain.embeddings.base import Embeddings
from langchain.schema.language_model import BaseLanguageModel
from langchain.text_splitter import (
    CharacterTextSplitter,
    RecursiveCharacterTextSplitter,
)
from langchain.tools.base import BaseTool
from langchain.vectorstores import FAISS
from langchain.vectorstores.utils import DistanceStrategy
from playwright.async_api import async_playwright
from pydantic import BaseModel, Field

ua = UserAgent()


class BrowseWebSiteInput(BaseModel):
    url: str = Field(..., description="The URL to visit")


class BrowseWebSiteTool(BaseTool):
    # embeddings: Embeddings
    # llm: BaseLanguageModel
    name: str = "browse_website"
    description: str = "Browses a Website"
    args_schema: Type[BaseModel] = BrowseWebSiteInput

    def _run(
        self,
        url: str,
        run_manager: CallbackManagerForToolRun | None = None,
    ) -> str:
        response = requests.get(url, headers={"User-Agent": ua.random})
        content_type = response.headers["content-type"]
        if "text/html" in content_type:
            soup = BeautifulSoup(response.text, "html.parser")
            for tag in soup.find_all(True):
                if tag.name in ["header", "footer"]:
                    tag.decompose()
                elif len(tag.get_text(strip=True)) == 0:
                    tag.decompose()

            md = html2text(soup.prettify(), bodywidth=1000000)

            # import tiktoken
            # encoding = tiktoken.get_encoding("cl100k_base")
            # num_tokens = len(encoding.encode(md))
            # print(num_tokens)

            return md
        elif "application/json" in content_type:
            return response.text
        elif "application/pdf" in content_type:
            return "無法讀取json"
        else:
            return response.text

    # async def _arun(
    #     self,
    #     url: str,
    #     question: str,
    #     run_manager: AsyncCallbackManagerForToolRun | None = None,
    # ) -> str:
    #     try:
    #         async with aiohttp.ClientSession() as session:
    #             async with session.get(
    #                 url, headers={"User-Agent": ua.random}
    #             ) as response:
    #                 if response.content_type == "text/html":
    #                     async with async_playwright() as p:
    #                         browser = await p.chromium.launch(headless=False)
    #                         page = await browser.new_page()
    #                         await page.goto(url)
    #                         html = await page.content()
    #                         await browser.close()

    #                     text = html2text(html)
    #                     text_splitter = RecursiveCharacterTextSplitter(
    #                         chunk_size=2000, chunk_overlap=100
    #                     )
    #                     documents = text_splitter.split_documents(
    #                         [Document(page_content=text)]
    #                     )
    #                     for i, document in enumerate(documents):
    #                         document.metadata["page"] = i

    #                 # elif response.content_type == 'application/json':
    #                 #     pass
    #                 elif response.content_type == "application/pdf":
    #                     loaders = [PyMuPDFLoader(url)]
    #                     draft_documents = []
    #                     for l in loaders:
    #                         draft_documents.extend(l.load())  # research async load
    #                     # text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=100)
    #                     text_splitter = CharacterTextSplitter.from_tiktoken_encoder(
    #                         chunk_size=2000, chunk_overlap=0
    #                     )
    #                     documents = []
    #                     temporary_document = Document(page_content="")
    #                     start_page = draft_documents[0].metadata["page"]
    #                     for draft_document in draft_documents:
    #                         splited_documents = text_splitter.split_documents(
    #                             [Document(page_content=draft_document.page_content)]
    #                         )
    #                         for splited_document in splited_documents:
    #                             if (
    #                                 self.llm.get_num_tokens(
    #                                     splited_document.page_content
    #                                 )
    #                                 + self.llm.get_num_tokens(
    #                                     temporary_document.page_content
    #                                 )
    #                                 < 2000
    #                             ):  # chunk size = 2000
    #                                 temporary_document.page_content += (
    #                                     f"{splited_document.page_content}\n"
    #                                 )

    #                             else:
    #                                 temporary_document.metadata["source"] = url
    #                                 temporary_document.metadata[
    #                                     "page"
    #                                 ] = f'{start_page}-{draft_document.metadata["page"]}'
    #                                 documents.append(temporary_document)
    #                                 start_page = draft_document.metadata["page"]
    #                                 temporary_document = Document(
    #                                     page_content=splited_document.page_content
    #                                 )

    #                     temporary_document.metadata["source"] = url
    #                     temporary_document.metadata[
    #                         "page"
    #                     ] = f'{start_page}-{draft_documents[-1].metadata["page"]}'
    #                     documents.append(temporary_document)

    #                 len_documents = len(documents)
    #                 l = 16  # document embedding size need to < 16
    #                 vectorstore = FAISS.from_documents(
    #                     documents[0:l],
    #                     self.embeddings,
    #                     distance_strategy=DistanceStrategy.COSINE,
    #                 )
    #                 for i in range(l, len_documents - l, l):
    #                     vectorstore.add_documents(documents[i : i + l])
    #                 document_prompt = PromptTemplate(
    #                     template="========Page {page}========\n{page_content}\n================",
    #                     input_variables=["page_content", "page"],
    #                 )
    #                 qa_chain = create_qa_with_structure_chain(
    #                     self.llm, AnswerWithSources, verbose=self.llm.verbose
    #                 )
    #                 combine_documents_chain = StuffDocumentsChain(
    #                     llm_chain=qa_chain,
    #                     document_variable_name="context",
    #                     document_prompt=document_prompt,
    #                 )
    #                 retrieval_qa = RetrievalQA(
    #                     retriever=vectorstore.as_retriever(search_kwargs={"k": 3}),
    #                     combine_documents_chain=combine_documents_chain,
    #                 )
    #                 r = await retrieval_qa.arun(question)
    #                 return json.dumps(r)
    #     except:
    #         return ""
