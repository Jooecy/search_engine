# python 3.6

"""网络爬虫和搜索引擎

"""

def quick_sort_pages(ranks, pages):
    if not pages or len(pages) <= 1:
        return pages
    else:
        pivot = ranks[pages[0]]
        worse = []
        better = []
        for page in pages[1:]:
            if ranks[page] <= pivot:
                worse.append(page)
            else:
                better.append(page)
    return quick_sort_pages(ranks, better) + [pages[0]] + quick_sort_pages(ranks, worse)

def ordered_search(index, ranks, keyword):
    pages = lookup(index, keyword)
    return quick_sort_pages(ranks, pages)

def lucky_search(index, ranks, keyword):
    """找到最佳匹配结果

    """
    pages = lookup(index, keyword)
    if not pages:
        return None
    best_page = pages[0]
    for candidate in pages:
        if ranks[candidate] > ranks[best_page]:
            best_page = candidate
    return best_page

def compute_ranks(graph):
    """page rank algorithm

    rank(page, 0) = 1/npages
    rank(page, t) = (1-d)/npages 
                  + sum (d * rank(p, t - 1) / number of outlinks from p) 
                  over all pages p that link to this page

    args:
       graph:  {page: [all urls in this page]}

    return:
       rank: {page: rank value}
    """
    d = 0.8 # damping factor
    numloops = 10
    
    ranks = {}
    npages = len(graph)
    for page in graph:
        ranks[page] = 1.0 / npages
    
    for i in range(0, numloops):
        newranks = {}
        for page in graph:
            newrank = (1 - d) / npages
            for node in graph:
                if page in graph[node]:
                    newrank += d * ranks[node] / len(graph[node])
            
            newranks[page] = newrank
        ranks = newranks
    return ranks



cache = {
   'http://udacity.com/cs101x/urank/index.html': """<html>
<body>
<h1>Dave's Cooking Algorithms</h1>
<p>
Here are my favorite recipies:
<ul>
<li> <a href="http://udacity.com/cs101x/urank/hummus.html">Hummus Recipe</a>
<li> <a href="http://udacity.com/cs101x/urank/arsenic.html">World's Best Hummus</a>
<li> <a href="http://udacity.com/cs101x/urank/kathleen.html">Kathleen's Hummus Recipe</a>
</ul>

For more expert opinions, check out the 
<a href="http://udacity.com/cs101x/urank/nickel.html">Nickel Chef</a> 
and <a href="http://udacity.com/cs101x/urank/zinc.html">Zinc Chef</a>.
</body>
</html>






""", 
   'http://udacity.com/cs101x/urank/zinc.html': """<html>
<body>
<h1>The Zinc Chef</h1>
<p>
I learned everything I know from 
<a href="http://udacity.com/cs101x/urank/nickel.html">the Nickel Chef</a>.
</p>
<p>
For great hummus, try 
<a href="http://udacity.com/cs101x/urank/arsenic.html">this recipe</a>.

</body>
</html>






""", 
   'http://udacity.com/cs101x/urank/nickel.html': """<html>
<body>
<h1>The Nickel Chef</h1>
<p>
This is the
<a href="http://udacity.com/cs101x/urank/kathleen.html">
best Hummus recipe!
</a>

</body>
</html>






""", 
   'http://udacity.com/cs101x/urank/kathleen.html': """<html>
<body>
<h1>
Kathleen's Hummus Recipe
</h1>
<p>

<ol>
<li> Open a can of garbonzo beans.
<li> Crush them in a blender.
<li> Add 3 tablesppons of tahini sauce.
<li> Squeeze in one lemon.
<li> Add salt, pepper, and buttercream frosting to taste.
</ol>

</body>
</html>

""", 
   'http://udacity.com/cs101x/urank/arsenic.html': """<html>
<body>
<h1>
The Arsenic Chef's World Famous Hummus Recipe
</h1>
<p>

<ol>
<li> Kidnap the <a href="http://udacity.com/cs101x/urank/nickel.html">Nickel Chef</a>.
<li> Force her to make hummus for you.
</ol>

</body>
</html>

""", 
   'http://udacity.com/cs101x/urank/hummus.html': """<html>
<body>
<h1>
Hummus Recipe
</h1>
<p>

<ol>
<li> Go to the store and buy a container of hummus.
<li> Open it.
</ol>

</body>
</html>




""", 
}


def crawl_web(seed):
    """爬取网页

    以seed起始开始爬取网页，从seed的网页内容中收集链接，然后再从链接中的页面中继续收集链接

    参数列表:
       seed: 种子url，即首个开始搜索的网页

    返回值:
        index: {keyword: [url,url...]}
        graph: {page: [all url in this page]}

    异常:

    """
    tocrawl = [seed]
    crawled = []
    graph = {}  # <url>, [list of pages it links to]
    index = {} 
    while tocrawl: 
        page = tocrawl.pop()
        if page not in crawled:
            content = get_page(page)
            add_page_to_index(index, page, content)
            outlinks = get_all_links(content)
            
            
            graph[page] = outlinks
            
            
            union(tocrawl, outlinks)
            crawled.append(page)
    return index, graph


def get_page(url):
    # TODO(zx): 通过urllib库获取真实的internet页面
    if url in cache:
        return cache[url]
    else:
        return None
    
def get_next_target(page):
    """从页面内容中获取下一个网页链接

    查找页面内容中的a元素(<a href="url">some link info</a>), 提取其中的url

    args:
        page: 网页的内容或者其中的一部分
    return:
        url: page中的第一个网页链接，找不到链接返回None
        end_quote: page中url结尾的"\""的位置，找不到链接返回0

    """
    start_link = page.find('<a href=')
    if start_link == -1: 
        return None, 0
    start_quote = page.find('"', start_link)
    end_quote = page.find('"', start_quote + 1)
    url = page[start_quote + 1:end_quote]
    return url, end_quote

def get_all_links(page):
    """从页面内容中获取所有网页链接

    查找页面内容中的所有a元素(<a href="url">some link info</a>), 提取其中的url

    args:
        page: 网页的内容
    return:
        links: 该页面内容所包含的所有url列表
    """
    links = []
    while True:
        url, endpos = get_next_target(page)
        if url:
            links.append(url)
            page = page[endpos:]
        else:
            break
    return links


def union(a, b):
    """把b中和a不重复的项添加至a

    args:
        a,b: 列表
    """
    for e in b:
        if e not in a:
            a.append(e)

def add_page_to_index(index, url, content):
    """将网页内容包含的单词以及对应的url添加至index字典

    args:
        index: {keyword: [url,url...]}
        url: 网页链接
        content: 网页内容
    """
    words = content.split()
    for word in words:
        add_to_index(index, word, url)
        
def add_to_index(index, keyword, url):
    """将keyword及对应的url添加到index字典中

    args:
        index: {keyword: [url,url...]}
        keyword: 关键词 string
        url: 网页链接
    """
    if keyword in index:
        index[keyword].append(url)
    else:
        index[keyword] = [url]

def lookup(index, keyword):
    """查询关键字匹配的url

    args:
        index: 保存了keyword和对应url的字典
        keyword: 要查询的关键词

    return:
        url: keyword对应的url列表
    """
    if keyword in index:
        return index[keyword]
    else:
        return None


if __name__ == "__main__":
    index, graph = crawl_web('http://udacity.com/cs101x/urank/index.html')
    ranks = compute_ranks(graph)

    #print(ranks)

    #>>> {'http://udacity.com/cs101x/urank/kathleen.html': 0.11661866666666663,
    #'http://udacity.com/cs101x/urank/zinc.html': 0.038666666666666655,
    #'http://udacity.com/cs101x/urank/hummus.html': 0.038666666666666655,
    #'http://udacity.com/cs101x/urank/arsenic.html': 0.054133333333333325,
    #'http://udacity.com/cs101x/urank/index.html': 0.033333333333333326,
    #'http://udacity.com/cs101x/urank/nickel.html': 0.09743999999999997}

    #print(lucky_search(index, ranks, 'Hummus'))
    #>>> http://udacity.com/cs101x/urank/kathleen.html

    #print(lucky_search(index, ranks, 'the'))
    #>>> http://udacity.com/cs101x/urank/nickel.html

    #print(lucky_search(index, ranks, 'babaganoush'))
    #>>> None

    print(ordered_search(index, ranks, 'Hummus'))
    #>>> ['http://udacity.com/cs101x/urank/kathleen.html',
    #    'http://udacity.com/cs101x/urank/nickel.html',
    #    'http://udacity.com/cs101x/urank/arsenic.html',
    #    'http://udacity.com/cs101x/urank/hummus.html',
    #    'http://udacity.com/cs101x/urank/index.html']
    
    print(ordered_search(index, ranks, 'the'))
    #>>> ['http://udacity.com/cs101x/urank/nickel.html',
    #    'http://udacity.com/cs101x/urank/arsenic.html',
    #    'http://udacity.com/cs101x/urank/hummus.html',
    #    'http://udacity.com/cs101x/urank/index.html']

    print(ordered_search(index, ranks, 'babaganoush')) 
    #>>> None
