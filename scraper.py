from playwright.async_api import async_playwright
import json

BASE_URL = "https://www.linkedin.com" 
LOGIN_URL = "https://www.linkedin.com/login"
NOT_FOUND_URL = "https://www.linkedin.com/404/"

async def login(page, email, password):
    await page.goto(LOGIN_URL)
    await page.fill("input[name=\"session_key\"]",email)
    await page.fill("input[name=\"session_password\"]",password)
    await page.click("button[type=\"submit\"]")


async def get_user_details(page,username):
    await page.goto(f"{BASE_URL}/in/{username}")

    await page.wait_for_selector("body")

    if page.url == NOT_FOUND_URL:
        return None

    await page.wait_for_selector("div#profile-content")

    first_section = await page.query_selector("main > section")

    name = await first_section.query_selector("h1")
    name = await name.text_content()
    name = name.strip()

    profile_picture = await first_section.query_selector(f"img.pv-top-card-profile-picture__image")
    if profile_picture is not None:
        profile_picture = await profile_picture.get_attribute("src")

    cover = await first_section.query_selector("div.profile-background-image")
    if cover is not None:
        cover = await cover.query_selector("img")
        if cover is not None:
            cover = await cover.get_attribute("src")

    left_panel = await first_section.query_selector("div.pv-text-details__left-panel")

    div_count = await left_panel.query_selector_all("div")
    div_count = len(div_count)

    if div_count >= 2:
        description = await left_panel.query_selector_all("div")
        description = description[1]
        description = await description.text_content()
        description = description.strip()

    right_panel = await first_section.query_selector("ul.pv-text-details__right-panel")

    if right_panel is None:
        return {
            "name": name,
            "description": description if div_count >= 2 else None,
            "companies": [],
            "cover": cover,
            "profile_picture": profile_picture
        }
    
    divs = await right_panel.query_selector_all("li")

    companies = []
    for div in divs:
        company = await div.query_selector("span")
        company = await company.text_content()
        company = company.strip()
        companies.append(company)

    user_details = {
        "name": name,
        "description": description if div_count >= 2 else None,
        "companies": companies,
        "cover": cover,
        "profile_picture": profile_picture
    }

    return user_details

async def scrape(email, password, username):
    async with async_playwright() as p:
        try:
            with open("cookies.json", "r") as f:
                cookies = json.loads(f.read())
        except FileNotFoundError:
            cookies = None

        browser = await p.chromium.launch(headless=True)
        
        if cookies:
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                storage_state={"cookies": cookies}
            )
        else:
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080}
            )
            page = await context.new_page()
            await login(page, email, password)

        page = await context.new_page()
        await page.goto(LOGIN_URL)
        if page.url == LOGIN_URL:
            await login(page, email, password)

        user_details = await get_user_details(page, username)
        
        cookies = await context.cookies()

        await page.close()
        await context.close()
        await browser.close()

        with open("cookies.json", "w") as f:
            f.write(json.dumps(cookies))

        return user_details
