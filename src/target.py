from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
import time
import random
import string
from faker import Faker
from itertools import cycle

CATCHALL = "thaanmail.com"
USER_AGENTS = [
    # Chrome on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Chrome on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    # Firefox on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:119.0) Gecko/20100101 Firefox/119.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:118.0) Gecko/20100101 Firefox/118.0",
    # Firefox on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:120.0) Gecko/20100101 Firefox/120.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:119.0) Gecko/20100101 Firefox/119.0",
    # Safari on Mac
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_0) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.5 Safari/605.1.15",
    # Edge on Windows
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0",
]


def main():
    # get number of accounts to create
    num_accounts = int(input("# of accounts to create: "))
    
    # flag to generate accounts
    generate = input("Generate accounts (y) or give profiles (n)? ").lower() == "y"
        
    # get proxies
    proxies = load_proxies()
    if not proxies:
        proxy_cycle = None
    else:
        proxy_cycle = cycle(proxies)    # set up proxy cycling
        
    with Stealth().use_sync(sync_playwright()) as p:
        # Launch the browser (set headless=False to see the browser UI)
        browser = p.chromium.launch(headless=False)

        for i in range(num_accounts):
             # get profile information
            profile = create_random_profile()
            
            if not generate:
                print(f"{profile['first']}:{profile['last']}:{profile['email']}:{profile['password']}:{profile['birthday']}")
                
                with open(f"resources/{CATCHALL}_target.txt", "a") as f:
                    f.write(f"{profile['email']}:{profile['password']}\n")
                continue

            # get next proxy from cycle
            proxy = next(proxy_cycle) if proxy_cycle else None

            context = browser.new_context(
                viewport={"width": random.randint(1260, 1400), "height": random.randint(700, 800)},
                user_agent=random.choice(USER_AGENTS),
                **({"proxy": proxy} if proxy else {})
            )

            # Open a new page
            page = context.new_page()

            # Navigate to a target website
            page.goto("https://www.target.com/")
            
            # click the sign in button
            wait_for_load(page)
            page.click("text=Sign in or create account")
            
            # enter catchall email
            wait_for_load(page)
            human_type(page, "#username", profile["email"])
            page.click("text=Continue")
            
            # enter profile information
            wait_for_load(page)
            # enter name
            human_type(page, "#firstname", profile["first"])
            human_type(page, "#lastname", profile["last"])
            # enter password
            page.click("#password-checkbox")
            human_type(page, "#password", profile["password"])
            page.click("#password-checkbox")
            
            page.click("#createAccount")
            
            # record email:password to resources folder, title of file is {catchall}_target.txt
            with open(f"resources/{CATCHALL}_target.txt", "a") as f:
                f.write(f"{profile['email']}:{profile['password']}\n")
            
            # final steps (not sure if needed)
            wait_for_load(page)
            human_type(page, "#birthdayField", profile["birthday"])
            page.click("#EnrollmentDontJoinButton")
            
            # make sure everything is saved before closing
            wait_for_load(page)
            context.close()
            
            print(f"{i + 1}/{num_accounts} - Created account: {profile['email']}:{profile['password']}")
            
        browser.close()


# helper scripts:
def human_type(page, selector: str, text: str):
    page.click(selector)
    for char in text:
        page.keyboard.type(char)
        time.sleep(random.uniform(0.05, 0.15))
        
def wait_for_load(page):
    # page.wait_for_load_state("networkidle")
    page.wait_for_load_state("domcontentloaded")
    page.wait_for_load_state("load")
    
def pause():
    while True:
        time.sleep(1)
        
def get_random_user():
    fake = Faker("en_US")

    first = fake.first_name()
    last = fake.last_name()
    birthday = fake.date_of_birth(minimum_age=18, maximum_age=80).strftime("%m/%d")
    return first, last, birthday

def create_random_email(first, last):
    random_string = ''.join(random.choices(string.digits, k=2))
    email = f"{first.lower()}_{last.lower()}{random_string}@{CATCHALL}"
    return email

def create_random_password():
    characters = string.ascii_letters + string.digits + "!@#$%^&*()"
    password = ''.join(random.choices(characters, k=12))
    return password

def create_random_profile():
    first, last, birthday = get_random_user()
    email = create_random_email(first, last)
    password = "8989Bolor"
    return {
        "first": first,
        "last": last,
        "birthday": birthday,
        "email": email,
        "password": password
    }
    
def load_proxies():
    proxies = []
    with open("resources/proxies.txt", "r") as f:
        for line in f:
            line = line.strip()
            if line:
                host, port, user, password = line.split(":")
                proxies.append({
                    "server": f"http://{host}:{port}",
                    "username": user,
                    "password": password
                })
    return proxies


    
if __name__ == "__main__":
    main()