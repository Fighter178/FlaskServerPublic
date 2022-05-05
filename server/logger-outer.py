import requests as reqs
def run_get():
    try:
        r = reqs.get(input("Enter URL: "), verify=False)
        print(f"URL {r.url}\n")
        print(f"Status Code: {r.status_code}\n")
        print(f"Content: {r.content}.decdoe()\n")
        print(f"Headers: {r.headers}\n")  
        print(f"Encoding: {r.encoding}\n")
        print(f"Cookies {r.cookies}\n")
        print(f"Elapsed: {r.elapsed}\n")
        try: 
                r.cookies.clear()
        except Exception as e:
            print("ERROR: ")
            print(e)
            if input("Go Again? (Y/N): ") == "y":
                run_get()
        if input("Go Again? (Y/N): ") == "y":
            run_get()
    except Exception as e:
        print("ERROR: ")
        print(e)
        if input("Try Again? (Y/N): ") == "y":
            run_post()
def run_post(data='data'):
    try:
        r = reqs.post(input("Enter URL: "), data="{'csrf_token', 'c1b5ed9b2fbe129ecee4675e4853cf31d4f407f1fac03d25e1c35cd22231009d'}", verify=False)
        print(f"URL {r.url}\n")
        print(f"Status Code: {r.status_code}\n")
        print(f"Content: {r.content}.decdoe()\n")
        print(f"Headers: {r.headers}\n")  
        print(f"Encoding: {r.encoding}\n")
        print(f"Cookies {r.cookies}\n")
        print(f"Elapsed: {r.elapsed}\n")
        if input("Clear all cookies (Y/N)? ") == "y":
            try: 
                r.cookies.clear(r.url)
            except Exception as e:
                print("ERROR: ")
                print(e)
                if input("Go Again? (Y/N): ") == "y":
                    run_post()
        if input("Go Again? (Y/N): ") == "y":
            run_post()
    except Exception as e:
        print("ERROR: ")
        print(e)
        if input("Try Again? (Y/N): ") == "y":
            run_post()
if input("Use POST(1) or GET(2)? ") == "1":
    run_post()
else: run_get()
