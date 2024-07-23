import re
import time

import google.generativeai as genai
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By


def get_code_2fa(key_2fa: str):
    """
    Lấy mã xác thực hai yếu tố (2FA) từ key 2fa

    Args:
        key_2fa (str): Truyền vào Key 2FA

    Returns:
        str: Mã xác thực 2FA.
    """
    url = f"https://2fa.live/tok/{key_2fa}"
    response = requests.get(url)
    data = response.json()
    token = data.get("token")
    return token


class AutoChrome:

    def __init__(self, enable_images: bool = False, enable_css: bool = True, headless: bool = False, proxy: str = ''):
        """
        ---
        Khởi tạo đối tượng AutoChrome.
        ---
        ### Các tham số:
            - enable_images (bool): Bật load hình ảnh(tắt sẽ load nhanh hơn)
            - enable_css (bool): Bật Load CSS
            - headless (bool): Chạy ẩn Chrome(Nhẹ hơn, có thể sẽ bị lỗi)
            - proxy (str): Proxy dạng IP:PORT
        """

        self.options = Options()
        self.options.add_argument("--disable-extensions")
        self.options.add_argument("--disable-gpu")
        self.options.add_argument('--deny-permission-prompts')
        self.options.add_argument('--disable-dev-shm-usage')
        self.options.add_argument('--disable-notifications')
        self.options.add_argument('--disable-infobars')
        self.options.add_argument(
            "--disable-blink-features=AutomationControlled")
        self.options.add_experimental_option("useAutomationExtension", False)
        self.options.add_experimental_option(
            "excludeSwitches", ['enable-automation'])
        self.options.add_experimental_option('prefs', {
            'credentials_enable_service': False,
            'profile': {
                'password_manager_enabled': False
            }
        })
        self.options.add_experimental_option(
            'excludeSwitches', ['disable-popup-blocking'])
        if headless:
            self.options.add_argument('--headless')
        if not enable_images:
            self.options.add_argument('--blink-settings=imagesEnabled=false')
            prefs = {"profile.managed_default_content_settings.images": 2}
            self.options.add_experimental_option("prefs", prefs)
        if not enable_css:
            self.options.add_experimental_option(
                "prefs", {"profile.managed_default_content_settings.stylesheets": 2})
            self.options.set_capability(
                'goog:loggingPrefs', {'browser': 'ALL'})
        if proxy:
            self.options.add_argument(f"--proxy-server={proxy}")
        self.driver = webdriver.Chrome(options=self.options)
        self.driver.get('https://mbasic.facebook.com')
        cookie = {
            'name': 'locale',
            'value': 'en_GB'
        }
        self.driver.add_cookie(cookie)

    def login(self, username: str, password: str, key_2fa: str):
        """
        ---
        Đăng nhập vào Facebook
        ---
        ### Các tham số:
            - username (str): Tên người Facebook.
            - password (str): Mật khẩu Facebook
            - key_2fa (str): KEY 2FA để lấy mã xác thực.
        ---
        ### Trả về:
            - str: "SUCCESS" nếu đăng nhập thành công, "FAILED" nếu sai pass hoặc sai 2FA
        """
        self.driver.get('https://mbasic.facebook.com')
        username_input = self.driver.find_element(By.ID, 'm_login_email')
        username_input.clear()
        username_input.send_keys(username)
        password_input = self.driver.find_element(By.NAME, 'pass')
        password_input.clear()
        password_input.send_keys(password)
        login_button = self.driver.find_element(By.NAME, 'login')
        login_button.click()
        if 'https://mbasic.facebook.com/login/' in self.driver.current_url:
            return "FAILED"
        if 'https://mbasic.facebook.com/checkpoint/?_rdr' in self.driver.current_url:
            code_2fa = get_code_2fa(key_2fa)
            code_2fa_input = self.driver.find_element(
                By.NAME, 'approvals_code')
            code_2fa_input.clear()
            code_2fa_input.send_keys(code_2fa)
            submit_button = self.driver.find_element(
                By.NAME, 'submit[Submit Code]')
            submit_button.click()
            if 'https://mbasic.facebook.com/login/checkpoint/' in self.driver.current_url:
                for i in range(10):
                    if i == 9:
                        return "FAILED"
                    try:
                        this_was_me_button = self.driver.find_element(
                            By.NAME, 'submit[This was me]')
                        this_was_me_button.click()
                    except:
                        pass
                    time.sleep(1)
                    submit_button = self.driver.find_element(
                        By.NAME, 'submit[Continue]')
                    submit_button.click()
                    if 'https://mbasic.facebook.com/login/checkpoint/' not in self.driver.current_url:
                        break
        return "SUCCESS"

    def search_group(self, keyword: str):
        """
        ---
        Tìm kiếm nhóm trên Facebook
        ---
        ### Các tham số:
            - keyword (str): Từ khóa tìm kiếm nhóm.
        ---
        ### Trả về:
            - str: "SUCCESS" nếu tìm kiếm thành công.
        """
        if " " in keyword:
            keyword = keyword.replace(" ", "+")
        self.driver.get(
            'https://mbasic.facebook.com/search/groups/?q=' + keyword)
        self.get_link(self.driver)
        for _ in range(2):
            see_more_pager_div = self.driver.find_element(
                By.ID, 'see_more_pager')
            see_more_pager_span = see_more_pager_div.find_element(
                By.TAG_NAME, 'span')
            see_more_pager_span.click()
            self.get_link(self.driver)
        return "SUCCESS"

    def get_link(self, driver):
        """
        ---
        Xuất ID Group
        ---
        ### Tham số:
            - driver (webdriver.Chrome): Đối tượng trình duyệt Chrome đang hoạt động.
        Returns:
            - str: "SUCCESS" nếu lấy liên kết thành công.
        """
        pattern = r"https://mbasic\.facebook\.com/groups/(\d+)"
        result_div = driver.find_element(By.ID, 'BrowseResultsContainer')
        tables = result_div.find_elements(By.TAG_NAME, 'table')
        links = [table.find_element(By.TAG_NAME, 'a') for table in tables]
        for link in links:
            url = link.get_attribute('href')
            match = re.search(pattern, url or '')
            if match:
                group_id = match.group(1)
                with open('group_id.txt', 'a') as f:
                    f.write(group_id + '\n')
        return "SUCCESS"

    def post_status(self, message: str, id: str, image_paths: list = []):
        """
        ---
        Spam bài lên group kèm và hình ảnh (nếu có).
        ---
        ### Tham số:
            - message (str): Nội dung bài viết.
            - id (str): ID của nhóm để đăng bài.
            - image_paths (list): Danh sách đường dẫn đến hình ảnh.

        ### Trả về:
            - str: "SUCCESS" nếu đăng bài viết thành công, "MAX_IMAGES" nếu số lượng hình ảnh vượt quá giới hạn.
        """
        id_group = id.replace('\n', '').replace('/\n', '')
        url = f'https://mbasic.facebook.com/groups/{id_group}'
        self.driver.get(url)
        view_more = self.driver.find_element(By.NAME, 'view_overview')
        view_more.click()
        if image_paths:
            image_button = self.driver.find_element(By.NAME, 'view_photo')
            image_button.click()
            for index, image_path in enumerate(image_paths):
                if len(image_paths) > 3:
                    return "MAX_IMAGES"
                image_input = self.driver.find_element(
                    By.NAME, f'file{index}')
                image_input.send_keys(image_path)
                time.sleep(1)
                send_button = self.driver.find_element(
                    By.NAME, 'add_photo_done')
                send_button.click()
        text_area = self.driver.find_element(By.NAME, 'xc_message')
        text_area.send_keys(message)
        post_button = self.driver.find_element(By.NAME, 'view_post')
        post_button.click()
        return "SUCCESS"


def gen_text(api, content):
    """
    ---
    Mix content
    ---
    ### Tham số:
        - api (str): API key Gemini [tại đây](https://aistudio.google.com/app/apikey?hl=vi)
        - content (str): Content cầnt thay đổi
    ---
    ### Trả về:
        - str: Content mới
    """
    genai.configure(api_key=api)
    generation_config = {
        "temperature": 2,
        "top_p": 0.95,
        "top_k": 64,
        "max_output_tokens": 1024,
        "response_mime_type": "text/plain",
    }

    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        generation_config=generation_config,  # type: ignore
    )

    chat_session = model.start_chat(
        history=[
            {
                "role": "user",
                "parts": [
                    "# Character\nBạn là một nhà tuyển dụng kiêm nhà sáng tạo nội dung chuyên nghiệp. Bạn giỏi viết các bài đăng tuyển dụng hấp dẫn và tuân thủ ngữ điệu, ngữ pháp và các quy chuẩn trên Facebook.\n\n## Skills\n### Skill 1: Tạo bài đăng tuyển dụng hấp dẫn\n- Hiểu yêu cầu công việc từ nhà tuyển dụng.\n- Tạo nội dung thu hút ứng viên có các kỹ năng phù hợp.\n- Đảm bảo ngữ điệu và ngữ pháp đúng chuẩn.\n- Nội dung bài đăng giới hạn trong 100 kí tự\n\n### Skill 2: Tối ưu hóa nội dung cho Facebook\n- Áp dụng chiến lược nội dung và hình ảnh phù hợp với đối tượng người đọc trên Facebook.\n- Sử dụng các hashtag, biểu tượng cảm xúc và lời kêu gọi hành động hiệu quả.\n\n### Skill 3: Luôn tạo bài đăng ngắn gọn\n- Thông tin cần bao gồm\n- Địa chỉ\n- Mức lương\n- Thông tin liên hệ(Zalo/Số điện thoại)\n\n## Constraints\n- Các bài đăng chỉ được tạo bằng tiếng Việt.\n- Không chứa nội dung gây tranh cãi hay phản cảm.\n- No yapping\n- Ngắn gọn, luôn áp dụng theo bài mẫu sau\n\n\n# Bài mẫu\nLàm nhà hàng lương 7 đến 8 triệu bao ăn ở tại Hà Nội . Liên hệ trực tiếp vs chủ . Sdt:0123456789..! Zalo :0123456789\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "OK, hãy đưa ra content cho tôi!",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Tuyển gấp nhân viên phục vụ tại quán cafe\n\n-  Địa chỉ: Quận 1, TP.HCM\n-  Lương: 6 - 8 triệu/tháng (bao ăn ở)\n-  Liên hệ: 0912345678 (Zalo/Điện thoại)",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "☕  Tuyển gấp nhân viên phục vụ cho quán cafe cực chill tại Quận 1! ☕\n\n🌟 Lương 6-8 triệu/tháng, bao ăn ở \n🌟  Liên hệ: 0912345678 (Zalo/Điện thoại)\n\n#tuyendung #nhanvienphucvu #quancafe #quan1 #tphcm\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Tuyển gấp nhân viên pha chế\n\n-  Địa chỉ: Quận 10, TP.HCM\n-  Lương: 7 - 9 triệu/tháng (bao ăn)\n-  Liên hệ:  0987654321 (Zalo)\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "☕️  Tuyển gấp nhân viên pha chế tài năng cho quán cafe tại Quận 10! ☕️\n\n🌟 Lương hấp dẫn 7-9 triệu/tháng, bao ăn.\n🌟 Liên hệ ngay: 0987654321 (Zalo)\n\n#tuyendung #nhanvienphache #quancafe #quan10 #tphcm \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "☕️ Tuyển gấp nhân viên pha chế tài năng cho quán cafe tại Quận 10! ☕️\n🌟 Lương hấp dẫn 7-9 triệu/tháng, bao ăn.\n🌟 Liên hệ ngay: 0987654321 (Zalo)\n#tuyendung #nhanvienphache #quancafe #quan10 #tphcm\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "☕️ Tìm đồng đội pha chế cho quán cafe tại Quận 10! ☕️\n🌟 Lương hấp dẫn 7-9 triệu/tháng, bao ăn ở\n🌟 Zalo/SDT: 0987654321 (Zalo)\n#tuyendung #nhanvienphache #quancafe #quan10 #tphcm\n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "☕️ Tuyển gấp nhân viên pha chế tài năng cho quán cafe tại Quận 10! ☕️\n🌟 Lương hấp dẫn 7-9 triệu/tháng, bao ăn.\n🌟 Liên hệ ngay: 0987654321 (Zalo)\n#tuyendung #nhanvienphache #quancafe #quan10 #tphcm",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "🎉  Tuyển gấp #NHÂNVIÊNPHACHE cho quán cafe chill tại Quận 10! 🎉\n\n👉 Lương 7-9 triệu/tháng, bao ăn.\n👉  Bạn có đam mê pha chế? Bạn muốn thử thách bản thân trong môi trường năng động? Nhanh tay liên hệ: 0987654321 (Zalo).\n\n#tuyendung #quancafe #quan10 #tphcm \n",
                ],
            },
            {
                "role": "user",
                "parts": [
                    "Làm nhà hàng lương 7 đến 8 triệu bao ăn ở tại Hà Nội . Liên hệ trực tiếp vs chủ . Sdt:0123456789..! Zalo :0123456789\n",
                ],
            },
            {
                "role": "model",
                "parts": [
                    "💪  Tuyển gấp nhân viên nhà hàng tại Hà Nội! 💪\n\n💸 Lương 7-8 triệu/tháng, bao ăn ở\n📞  Liên hệ trực tiếp với chủ: 0123456789 (Zalo/SĐT)\n#tuyendung #nhanvien #nhahang #hanoi \n",
                ],
            },
        ]
    )
    response = chat_session.send_message(content)
    return response.text


# Ví dụ sử dụng lớp AutoChrome:
# chrome = AutoChrome()
# chrome.login('100080375493485', 'sFuLBTIcV2', 'XCKBODK3ZRMIGRO7E7IUQYXD5JXCZO33')
# chrome.search_group('Con Meo')
# with open('group_id.txt', 'r') as f:
#     for line in f:
#         chrome.post_status('Con Meo', line)
