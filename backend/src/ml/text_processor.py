from bs4 import BeautifulSoup


from .base import BaseProcessor

class TextProcessor(BaseProcessor):
    def process(self,ocr_result)->list[dict]: #[{markdown:str,json_layout:list[JSON],page:list[list[str]]}]
        text = ""
        blocks = []
        for page in ocr_result:
            html = page.get("markdown","")
            json_layout = page.get("json_layout","")
            for block in json_layout:
                conf = block.get("conf",0)
                html = block.get("text","")
                lines = "\n".join(["\t".join(row) for row in self.parse(html)]) 
                text += lines + "\n"
                blocks.append({'conf':conf,'text':lines})        
        return text,blocks
    def parse(self,html)->list[list[str]]:
        text = []
        soup = BeautifulSoup(html,"html.parser")
        tables = soup.find_all("table")
        if tables:
            for table in tables:
                for row in table.find_all("tr"):
                    extracted_row =[]
                    th = row.find_all("th")
                    td = row.find_all("td")
                    if th:
                        for cell in th:
                            extracted_row.append(cell.get_text(strip=True))
                    if td:
                        for cell in td:
                            extracted_row.append(cell.get_text(strip=True))
                    text.append(extracted_row)
        direct_text = soup.find_all(string=True, recursive=False)
        if direct_text is not None:
            cleaned_texts  = [text.strip() for text in direct_text if text.strip()]
            text.append(direct_text)
        return text
