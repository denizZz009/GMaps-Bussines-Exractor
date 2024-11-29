from playwright.sync_api import sync_playwright
from dataclasses import dataclass, asdict, field
import pandas as pd
import argparse

l1 = []
l2 = []

# Değişkenler için başlangıç değerleri
Name = ""
Address = ""
Website = ""
Phone_Number = ""
Reviews_Count = 0
Reviews_Average = 0
Store_Shopping = ""
In_Store_Pickup = ""
Store_Delivery = ""
Place_Type = ""
Opens_At = ""
Introduction = ""

names_list = []
address_list = []
website_list = []
phones_list = []
reviews_c_list = []
reviews_a_list = []
store_s_list = []
in_store_list = []
store_del_list = []
place_t_list = []
open_list = []
intro_list = []

def extract_data(xpath, data_list, page):
    if page.locator(xpath).count() > 0:
        data = page.locator(xpath).inner_text()
    else:
        data = ""
    # Türkçe karakter desteği sağlamak için veriyi normalize etme
    data = data.replace("ı", "i").replace("İ", "I").replace("ş", "s").replace("Ş", "S").replace("ç", "c").replace("Ç", "C").replace("ğ", "g").replace("Ğ", "G").replace("ö", "o").replace("Ö", "O").replace("ü", "u").replace("Ü", "U")
    data_list.append(data)

def main():
    with sync_playwright() as p:
        browser = p.chromium.launch(executable_path=r'C:\Program Files\Google\Chrome\Application\chrome.exe', headless=False)
        page = browser.new_page()

        page.goto("https://www.google.com/maps/@32.9817464,70.1930781,3.67z?", timeout=46360000)
        page.wait_for_timeout(2100)

        page.locator('//input[@id="searchboxinput"]').fill(search_for)
        page.keyboard.press("Enter")
        page.wait_for_selector('//a[contains(@href, "https://www.google.com/maps/place")]')

        page.hover('//a[contains(@href, "https://www.google.com/maps/place")]')

        previously_counted = 0
        while True:
            page.mouse.wheel(0, 46360000)
            page.wait_for_timeout(1400)  # Timeout ayarı sayfanın tam olarak yüklenmesi için

            if (page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count() >= total):
                listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()[:total]
                listings = [listing.locator("xpath=..") for listing in listings]
                print(f"Toplam Bulunan: {len(listings)}")
                break
            else: 
                if (page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count() == previously_counted):
                    listings = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').all()
                    print(f"Tüm listeye ulaşıldı\nToplam Bulunan: {len(listings)}")
                    break
                else:
                    previously_counted = page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count()
                    print(f"Şu An Bulunan: ", page.locator('//a[contains(@href, "https://www.google.com/maps/place")]').count())

        # Verileri çekme işlemi
        for listing in listings:
            listing.click()
            page.wait_for_selector('//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]')
            
            name_xpath = '//div[@class="TIHn2 "]//h1[@class="DUwDvf lfPIob"]'
            address_xpath = '//button[@data-item-id="address"]//div[contains(@class, "fontBodyMedium")]'
            website_xpath = '//a[@data-item-id="authority"]//div[contains(@class, "fontBodyMedium")]'
            phone_number_xpath = '//button[contains(@data-item-id, "phone:tel:")]//div[contains(@class, "fontBodyMedium")]'
            reviews_count_xpath = '//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span//span//span[@aria-label]'
            

            reviews_average_xpath = '//div[@class="TIHn2 "]//div[@class="fontBodyMedium dmRWX"]//div//span[@aria-hidden]'

            info1 = '//div[@class="LTs0Rc"][1]'  # mağaza
            info2 = '//div[@class="LTs0Rc"][2]'  # pickup
            info3 = '//div[@class="LTs0Rc"][3]'  # delivery
            opens_at_xpath = '//button[contains(@data-item-id, "oh")]//div[contains(@class, "fontBodyMedium")]'  # zaman
            opens_at_xpath2 = '//div[@class="MkV9"]//span[@class="ZDu9vd"]//span[2]'
            place_type_xpath = '//div[@class="LBgpqf"]//button[@class="DkEaL "]'  # mekan türü
            intro_xpath = '//div[@class="WeS02d fontBodyMedium"]//div[@class="PYvSYb "]'

            # Tanıtımı al
            if page.locator(intro_xpath).count() > 0:
                Introduction = page.locator(intro_xpath).inner_text()
                intro_list.append(Introduction)
            else:
                Introduction = ""
                intro_list.append("Bulunamadı")
            
            # Yorum Sayısı
            if page.locator(reviews_count_xpath).count() > 0:
                temp = page.locator(reviews_count_xpath).inner_text()
                temp = temp.replace('(', '').replace(')', '').replace(',', '').replace('.', '')
                Reviews_Count = int(temp)
                reviews_c_list.append(Reviews_Count)
            else:
                Reviews_Count = ""
                reviews_c_list.append(Reviews_Count)

            # Yorum Ortalaması
            if page.locator(reviews_average_xpath).count() > 0:
                temp = page.locator(reviews_average_xpath).nth(0).inner_text()  # İlk öğeyi almak için .nth(0)
                temp = temp.replace(' ', '').replace(',', '.')
                try:
                    Reviews_Average = float(temp)
                except ValueError:
                    Reviews_Average = 0.0  # Hata durumunda varsayılan değer
                reviews_a_list.append(Reviews_Average)
            else:
                Reviews_Average = ""
                reviews_a_list.append(Reviews_Average)

            # Mağaza Bilgileri (Alışveriş, Pickup, Teslimat)
            for info_xpath, store_list in zip([info1, info2, info3], [store_s_list, in_store_list, store_del_list]):
                if page.locator(info_xpath).count() > 0:
                    temp = page.locator(info_xpath).inner_text()
                    temp = temp.split('·')
                    check = temp[1].replace("\n", "")
                    if 'shop' in check:
                        store_list.append("Evet")
                    elif 'pickup' in check:
                        store_list.append("Evet")
                    elif 'delivery' in check:
                        store_list.append("Evet")
                else:
                    store_list.append("Hayır")
            
            # Çalışma Saatleri
            if page.locator(opens_at_xpath).count() > 0:
                opens = page.locator(opens_at_xpath).inner_text()
                opens = opens.split('⋅')
                opens = opens[1] if len(opens) > 1 else opens[0]
                opens = opens.replace("\u202f", "")
                Opens_At = opens
                open_list.append(Opens_At)
            else:
                Opens_At = ""
                open_list.append(Opens_At)

            if page.locator(opens_at_xpath2).count() > 0:
                opens = page.locator(opens_at_xpath2).inner_text()
                opens = opens.split('⋅')[1].replace("\u202f", "")
                open_list.append(opens)

            # Diğer verileri çek
            extract_data(name_xpath, names_list, page)
            extract_data(address_xpath, address_list, page)
            extract_data(website_xpath, website_list, page)
            extract_data(phone_number_xpath, phones_list, page)
            extract_data(place_type_xpath, place_t_list, page)

        # Sonuçları CSV'ye kaydetme
        df = pd.DataFrame(list(zip(names_list, website_list, intro_list, phones_list, address_list, reviews_c_list, reviews_a_list, store_s_list, in_store_list, store_del_list, place_t_list, open_list)), columns = ['İsimler', 'Website', 'Tanıtım', 'Telefon Numarası', 'Adres', 'Yorum Sayısı', 'Ortalama Yorum', 'Mağaza Alışveriş', 'In-Store Pickup', 'Teslimat', 'Tür', 'Çalışma Saatleri'])
        
        # Aynı değeri içeren kolonları sil
        for column in df.columns:
            if df[column].nunique() == 1:
                df.drop(column, axis=1, inplace=True)
        
        # UTF-8 kodlamasıyla CSV dosyasına kaydet
        df.to_csv(r'logs.csv', index=False, encoding='utf-8-sig')  
        browser.close()
        print(df.head())

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("-s", "--search", type=str)
    parser.add_argument("-t", "--total", type=int)
    args = parser.parse_args()

    if args.search:
        search_for = args.search
    else:
        search_for = input('Enter your search term: ')

    if args.total:
        total = args.total
    else:
        total = int(input('Enter the desired total number of entries: '))

    main()
