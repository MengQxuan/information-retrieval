import scrapy
import re
import csv

class NKUSpider(scrapy.Spider):
    name = "nku"
    allowed_domains = ["nankai.edu.cn"]
    start_urls = ["http://www.nankai.edu.cn/"]#http://www.nankai.edu.cn/

    def __init__(self, *args, **kwargs):
        super(NKUSpider, self).__init__(*args, **kwargs)
        self.output_file = "nku_output.csv"  # CSV 文件名
        # 初始化 CSV 文件，写入标题行
        with open(self.output_file, "w", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow(["title", "url", "text", "linksurl"])

    def parse(self, response):
        # 提取网页标题
        title = response.xpath("//title/text()").get(default="Untitled")
        
        # 提取正文内容，仅保留有效文本
        raw_text = response.xpath("//body//*[not(self::script or self::style)]/text()").getall()
        clean_content = self.clean_text(" ".join(raw_text))

        # 提取链接
        links = response.xpath("//a[@href]/@href").extract()
        full_links = []
        for link in links:
            if link.startswith("/"):  # 处理相对路径
                link = response.urljoin(link)
            if self.allowed_domains[0] in link:  # 确保只抓取允许的域
                full_links.append(link)
        linksurl = "; ".join(full_links)  # 用分号分隔所有链接

        # 保存数据到 CSV
        self.save_to_csv(title, response.url, clean_content, linksurl)

        # 继续爬取链接
        for link in full_links:
            yield scrapy.Request(link, callback=self.parse)

    def save_to_csv(self, title, url, text, linksurl):
        """
        保存爬取到的数据到 CSV 文件
        """
        with open(self.output_file, "a", newline="", encoding="utf-8-sig") as f:
            writer = csv.writer(f)
            writer.writerow([title, url, text, linksurl])

    def clean_text(self, text):
        """
        清理无效换行、缩进和多余空格的文本内容
        """
        # 替换换行符和缩进为空格
        text = text.replace("\n", " ").replace("\r", " ").strip()
        # 使用正则去除多余的空格
        text = re.sub(r'\s+', ' ', text)
        return text
