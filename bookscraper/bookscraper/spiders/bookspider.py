from typing import Any
import scrapy
from scrapy.http import Response


class BookspiderSpider(scrapy.Spider):
    name = "bookspider"
    allowed_domains = ["books.toscrape.com"]
    start_urls = ["https://books.toscrape.com"]

    def parse(self, response):
        books = response.css('article.product_pod')
        
        for book in books:
            relative_url = book.css("a::attr(href)").get()
            if 'catalogue/' in relative_url:
                book_url = "https://books.toscrape.com/" + relative_url
            else:
                 book_url = "https://books.toscrape.com/catalogue/" + relative_url
            
            yield response.follow(book_url, callback = self.parse_book_page)

    
        next_page = response.css("li.next a::attr(href)").get()
        if next_page is not None:
            if "catalogue/" not in next_page:
                next_page = "catalogue/" + next_page
            

            next_page_url = "https://books.toscrape.com/" + next_page
            yield response.follow(next_page_url, callback = self.parse)

    def parse_book_page(self,response):
        book_page = response.css('article.product_page')
        rows_data = book_page.css('table.table-striped tr td::text').getall()
        rating = book_page.css("p.star-rating::attr(class)").get()

        yield{
            "Genre": book_page.xpath("//ul[@class='breadcrumb']/li[@class='active']/preceding-sibling::li[1]/a/text()").get(),
            'UPC': rows_data[0],
            'Product Type': rows_data[1],
            'Price(excl Tax)': rows_data[2],
            'Price(incl Tax)': rows_data[3],
            'Tax': rows_data[4],
            'Availability': rows_data[5],
            "Reviews": rows_data[6],
            "Rating": rating.split()[1]
        }
        