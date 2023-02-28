from scraper import scrape
import streamlit as st
from dotenv import load_dotenv
import os
import asyncio

load_dotenv()

EMAIL = os.getenv("EMAIL")
PASSWORD = os.getenv("PASSWORD")

# install playwright
os.system("playwright install")

async def main():
    user_details = await scrape(EMAIL, PASSWORD, username)
    return user_details

st.title("Linkedin Scraper")
st.write("This is a simple scraper that scrapes Linkedin user details.")

username = st.text_input("Username")

if st.button("Scrape"):
    if os.name == "nt":
        loop = asyncio.ProactorEventLoop()
        asyncio.set_event_loop(loop)

        user_details = loop.run_until_complete(main())
    else:
        user_details = asyncio.run(main())

    if user_details is None:
        st.error("User not found.")
        st.stop()

    name = user_details["name"]
    description = user_details["description"]
    cover = user_details["cover"]
    profile_picture = user_details["profile_picture"]
    companies = user_details["companies"]

    if cover:
        st.image(cover)
    row1_1, row1_2 = st.columns([1, 2])
    with row1_1:
        if profile_picture:
            st.image(profile_picture)
    with row1_2:
        st.title(name)
        st.write(description)

        st.subheader("Companies")
        for company in companies:
            st.markdown(f"- {company}")

    