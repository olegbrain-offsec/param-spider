#!/usr/bin/env python3
from urllib.parse import unquote 
import requests
import re, random
import argparse
import os
import errno
import time 
start_time = time.time()

# Param extractor
def param_extract(response, level, black_list, placeholder):

    parsed = list(set(re.findall(r'.*?:\/\/.*\?.*\=[^$]' , response)))
    final_uris = []
        
    for i in parsed:
        delim = i.find('=')
        second_delim = i.find('=', i.find('=') + 1)
        if len(black_list) > 0:
            words_re = re.compile("|".join(black_list))
            if not words_re.search(i):
                final_uris.append((i[:delim+1] + placeholder))
                if level == 'high':
                    final_uris.append(i[:second_delim+1] + placeholder)
        else:
            final_uris.append((i[:delim+1] + placeholder))
            if level == 'high': final_uris.append(i[:second_delim+1] + placeholder)    
    return list(set(final_uris))

# Connector 
def connector(url):
    result = False
    user_agent_list = [
   #Chrome
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/44.0.2403.157 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.113 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36',
    #Firefox
    'Mozilla/4.0 (compatible; MSIE 9.0; Windows NT 6.1)',
    'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; WOW64; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 6.2; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.0; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.3; WOW64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 9.0; Windows NT 6.1; Trident/5.0)',
    'Mozilla/5.0 (Windows NT 6.1; Win64; x64; Trident/7.0; rv:11.0) like Gecko',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; WOW64; Trident/6.0)',
    'Mozilla/5.0 (compatible; MSIE 10.0; Windows NT 6.1; Trident/6.0)',
    'Mozilla/4.0 (compatible; MSIE 8.0; Windows NT 5.1; Trident/4.0; .NET CLR 2.0.50727; .NET CLR 3.0.4506.2152; .NET CLR 3.5.30729)'
]
    user_agent = random.choice(user_agent_list)
    headers = {'User-Agent': user_agent}
 
    try:
            response = requests.get(url,headers=headers ,timeout=30)
            result = response.text
            retry = False
            response.raise_for_status()
    except requests.exceptions.ConnectionError as e:
            retry = True
            print("Can not connect to server. Retrying in 2-5 seconds.")
            time.sleep(random.randint(2,5))
    except requests.exceptions.Timeout as e:
            retry = True
            print("OOPS!! Timeout Error. Retrying in 2-5 seconds.")
            time.sleep(random.randint(2,5))
    except requests.exceptions.HTTPError as err:
            retry = True
            print("Error. Retrying in 2-5 seconds.")
            time.sleep(random.randint(2,5))
    except requests.exceptions.RequestException as e:
            retry = True
            print("Can not get target information")
    except KeyboardInterrupt as k:
            retry = False
            print("Interrupted by user")
            raise SystemExit(k)
    finally:
            return result, retry


# Save 
def save_func(final_urls , outfile , domain):
    if outfile:
        if "/" in outfile: filename = f'{outfile}'
        else : filename = f'output/{outfile}'
    else: filename = f"output/{domain}.txt"
    
    if os.path.exists(filename): os.remove(filename)
    if not os.path.exists(os.path.dirname(filename)):
        try:
            os.makedirs(os.path.dirname(filename))
        except OSError as exc: 
            if exc.errno != errno.EEXIST:
                raise
    
    for i in final_urls:
        with open(filename, "a" , encoding="utf-8") as f:
            f.write(i+"\n")


def main():
    banner = """

         ___                               _    __       
        / _ \\___ ________ ___ _  ___ ___  (_)__/ /__ ____
       / ___/ _ `/ __/ _ `/  ' \\(_-</ _ \\/ / _  / -_) __/
      /_/   \\_,_/_/  \\_,_/_/_/_/___/ .__/_/\\_,_/\\__/_/   
                                  /_/                                     
    """

    parser = argparse.ArgumentParser(description='ParamSpider a parameter discovery suite')
    parser.add_argument('-d','--domain' , help = 'Domain name of the taget [ex : hackerone.com]' , required=True)
    parser.add_argument('-s' ,'--subs' , help = 'Set False for no subs [ex : --subs False ]' , default=True)
    parser.add_argument('-l','--level' ,  help = 'For nested parameters [ex : --level high]')
    # parser.add_argument('-e','--exclude', help= 'extensions to exclude [ex --exclude php,aspx]')
    parser.add_argument('-o','--output' , help = 'Output file name [by default it is \'domain.txt\']')
    parser.add_argument('-p','--placeholder' , help = 'The string to add as a placeholder after the parameter name.', default = "FUZZ")
    parser.add_argument('-q', '--quiet', help='Do not print the results to the screen', action='store_true')
    parser.add_argument('-r', '--retries', help='Specify number of retries for 4xx and 5xx errors', default=3)
    args = parser.parse_args()

    if not args.quiet: print(banner)

    if args.subs == True or args.subs == " True" or args.subs == "True": url = f"https://web.archive.org/cdx/search/cdx?url=*.{args.domain}/*&output=txt&fl=original&collapse=urlkey&page=/"
    else: url = f"https://web.archive.org/cdx/search/cdx?url={args.domain}/*&output=txt&fl=original&collapse=urlkey&page=/"
    
    retry = True
    retries = 0
    while retry == True and retries <= int(args.retries):
             response, retry = connector(url)
             retry = retry
             retries += 1
    if response == False:
         return
    response = unquote(response)
   
    # for extensions to be excluded: change to args.exclude if you want to use argparse
    exclude = "png,jpg,gif,jpeg,swf,woff,svg,pdf,css,js,webp,woff,woff2,eot,ttf,otf,mp4,txt"
    black_list = []
    if exclude:
         if "," in exclude:
             black_list = exclude.split(",")
             for i in range(len(black_list)):
                 black_list[i] = "." + black_list[i]
         else: black_list.append("." + exclude)
    # else: black_list = [] # for blacklists
    # if exclude: print(f"[!] URLS containing these extensions will be excluded from the results   : {black_list}\u001b[0m\n")
      
    final_uris = param_extract(response , args.level , black_list, args.placeholder)
    for i in range(0,len(final_uris)):
        newstring = final_uris[i]
        newstring = re.sub(r'\?utm_[a-zA-Z_]*?=.*?\&','?', newstring)
        newstring = re.sub(r'\?utm_[a-zA-Z_]*?=[a-zA-Z0-9\.-_]*?$','',newstring)
        newstring = re.sub(r'\&utm_[a-zA-Z_]*?=[a-zA-Z0-9\.-_]*?&','&',newstring)
        newstring = re.sub(r'\&utm_[a-zA-Z_]*?=[a-zA-Z0-9\.-_]*?$','',newstring)
        # Delete port number and replace HTTP wnewstringth HTTPS
        if newstring.startswith('http://'): newstring = newstring.replace('http://','https://', 1)
        insecure_port = re.search(r'http.{0,}:\/\/.*?(:[0-9]*)', newstring)
        if insecure_port is not None: newstring = newstring.replace(insecure_port.group(1), '', 1)
        final_uris[i] = newstring
         
    save_func(final_uris , args.output , args.domain)

    if not args.quiet: print('\n'.join(final_uris))

    if args.output:
        if "/" in args.output: print(f"[+] Output is saved here: {args.output}, retries: {retries-1}, total urls: {len(final_uris)}" )
        else: print(f"[+] Output is saved here: output/{args.output}, retries: {retries-1}, total urls: {len(final_uris)}" )
    else: print(f"[+] Output is saved here: output/{args.domain}.txt, retries: {retries-1}, total urls: {len(final_uris)}")

if __name__ == "__main__":
    main()