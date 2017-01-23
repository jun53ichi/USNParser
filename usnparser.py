#coding: UTF-8

import sys
import urllib.request
from bs4 import BeautifulSoup

usn_url = "https://www.ubuntu.com/usn/"
usn_default_no = 'usn-3172-1'  # USN番号を指定
usn_sample_html = 'ubuntu.html'

detail_text=' The problem can be corrected by updating your system to the following\npackage version:'

# soupを取得
def get_soup(target):
    soup = 0
    if 'http' in target:
        # USNサイトからhtmlを取得
        html = urllib.request.urlopen(target).read()
        # HTML解析
        soup = BeautifulSoup(html, "html.parser")
    else:
        html = open(target, 'r').read()
        soup = BeautifulSoup(html, "html.parser")
    return soup

# RefernecesのCVE優先度を取得する
def get_cve_priority(href):
    soup = get_soup(href)
    # 最初のfieldクラスがPriority
#    return soup.find_all("div", "medium-value")[0].text

    for div in soup.find_all('div'):
        title = div.text
        if title == 'Priority':
            priority=div.find_next_sibling('div').text
            #print(priority)  #for debug
    return priority

# 一番高いレベルのPriorityを返す
def get_hieghest_priority(priorities):
    if 'High' in priorities:
        return 'High'
    elif 'Medium' in priorities:
        return 'Medium'
    elif 'Low' in priorities:
        return 'Low'
    else:
        return 'None'

# main
if __name__ == '__main__':
    args = sys.argv
    usn_no = usn_default_no
    if len(args) > 1:
        usn_no = args[1]
    soup = get_soup(usn_url + usn_no)
    #soup = get_soup(usn_sample_html)

    # 各項目の取得

    # 通知日
    h2 = soup.find('h2')
    print('Date:')
    print(h2.find_next_sibling('p').text)

    #対象Ubuntu版数
    h3 = soup.find('h3')    
    ul = h3.find_next_sibling('ul')
    lis = ul.find_all('li')
    print('Ubuntu version:')
    for li in lis:
        print(li.text)

    for h3 in soup.find_all('h3'):
        # Details
        title = h3.text
        if title == 'Details':
            print('Details:')
#            print(h3.find_next_sibling('p').text)
            # next_siblingだと改行(\n)がヒットしてしまうので次の<p>を探す

            p = h3
            while  True:
                p = p.find_next_sibling('p')
                if p.text == detail_text:
                    break
                print(p.text + '\n')

        #Update instructions
        elif title == 'Update instructions':
            print('Update instructions:')
            
            # <dl>の中に<dt>でUbuntuバージョン、さらに<dd>のなかに対象パッケージとバージョンがリストになっている
            # <dl>
            #     <dt>Ubuntuバージョン</dt>
            #     <dd>
            #         <a>パッケージ名
            #         <a>パッケージバージョン</a>
            #     </dd>
            # ・・・
            # </dl>            
            dls = h3.find_next_sibling('dl')
            lists = dls.find_all([ 'dt' , 'a' ])
            for a in lists:
                print(a.text)
                # パッケージ名
                # バージョン
                # の繰り返し形で表示

        # References
        elif title == 'References':
            print('References:')
            p = h3.find_next_sibling('p')
            # <p>の中にCVEへのリンクがリストになっている
            priorities = []
            for a in p.find_all('a'):
                print(a.text)
                #print(a.get('href'))  # URL取得
                priorities.append(get_cve_priority(a.get('href')))  # CVE優先度

        # Priority
            print ('Priority:')
            print(get_hieghest_priority(priorities))

        # Link
            print('Link:')
            print(usn_url + usn_no)
        
