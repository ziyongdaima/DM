
import sys, random, urllib3, time
from base.spider import Spider
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
sys.path.append('..')

class Spider(Spider):
    headers = {
        'User-Agent': 'Mozilla/5.0 (Linux; Android 12; SM-S9080 Build/V417IR; wv) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/101.0.4951.61 Safari/537.36;webank/h5face;webank/1.0;netType:NETWORK_WIFI;appVersion:815;packageName:com.jp3.pluginxg3',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Encoding': 'gzip, deflate',
        'x-requested-with': 'com.jp3.pluginxg3',
        'sec-fetch-site': 'cross-site',
        'sec-fetch-mode': 'cors',
        'sec-fetch-dest': 'empty',
        'accept-language': 'zh-CN,zh;q=0.9,en-US;q=0.7'
    }
    host = ''
    pic_domain = ''
    pic_domains = []
    CATE_NAME_LIST = ["短剧", "电视剧", "电影", "动漫", "综艺"]
    CATE_ID_LIST = ["67", "2", "1", "3", "4"]
    FILTER_MAP = {
        "category_id": ("cateId", "分类"),
        "type": ("class", "剧情"),
        "area": ("area", "地区"),
        "year": ("year", "年份"),
        "sort": ("by", "排序")
    }

    def init(self, extend=''):
        self.host = "https://api.ztcgi.com"
        if self.host:
            self._fetch_pic_domains(self.host)

    def _fetch_pic_domains(self, host):
        try:
            r = self.fetch(f'{host}/api/resourceDomainConfig', headers=self.headers, verify=False, timeout=2).json()
            if r.get('code') == 1:
                img_str = r.get('data', {}).get('imgDomain', '')
                if img_str:
                    self.pic_domains = [f"https://{d.strip()}" if not d.startswith('http') else d.strip() for d in img_str.split(',') if d.strip()]
                    self.pic_domain = self.pic_domains[0] if self.pic_domains else ''
        except Exception:
            pass

    def homeContent(self, filter):
        try:
            classes = []
            for name, cid in zip(self.CATE_NAME_LIST, self.CATE_ID_LIST):
                classes.append({"type_id": cid, "type_name": name})

            filters = {}
            main_cates = [c for c in classes if c["type_id"] != "99"]
            for cate in main_cates:
                tid = cate["type_id"]
                try:
                    res = self.fetch(f"{self.host}/api/crumb/filterOptions?fcate_pid={tid}", headers=self.headers, verify=False).json()
                    raw = res.get("data", [])
                    out = []
                    for item in raw:
                        k_api = item.get("key", "")
                        if k_api not in self.FILTER_MAP:
                            continue
                        k_front, name_show = self.FILTER_MAP[k_api]
                        opts = []
                        for opt in item.get("data", []):
                            opts.append({"n": opt.get("name", "未知"), "v": opt.get("id", "")})
                        if opts:
                            out.append({"key": k_front, "name": name_show, "value": opts})
                    filters[tid] = out
                except Exception:
                    filters[tid] = []

            resFenlei = self.fetch(f'{self.host}/api/term/home_fenlei', headers=self.headers, verify=False).json()
            tj_id = 88
            for i in resFenlei.get("data", []):
                if i.get("name") == "推荐":
                    tj_id = i.get("id", 88)
            resRec = self.fetch(f'{self.host}/api/dyTag/list?category_id={tj_id}', headers=self.headers, verify=False).json()
            videos = []
            for item in resRec.get("data", []):
                videos.extend(self.arr2vods(item.get("dataList", [])))

            return {"class": classes, "filters": filters, "list": videos}
        except Exception:
            return {"class": [], "filters": {}, "list": []}

    def categoryContent(self, tid, pg, filter, ext):
        videos = []
        pg = str(pg)
        sort_val = ext.get("by", "new") if isinstance(ext, dict) else "new"
        if tid == '99':
            if pg == '2':
                return {"list": videos, "page": pg}
            res = self.fetch(f'{self.host}/api/dyTag/list?category_id={tid}', headers=self.headers, verify=False).json()
            for i in res.get("data", []):
                videos.extend(self.arr2vods(i.get("dataList", []), tid))
        else:
            cateId = ext.get("cateId", "") if isinstance(ext, dict) else ""
            cls = ext.get("class", "") if isinstance(ext, dict) else ""
            area = ext.get("area", "") if isinstance(ext, dict) else ""
            year = ext.get("year", "") if isinstance(ext, dict) else ""
            if tid == "67":
                path = f"/api/crumb/shortList?fcate_pid={tid}&category_id={cateId}&type={cls}&area={area}&year={year}&sort={sort_val}&page={pg}"
            else:
                path = f"/api/crumb/list?fcate_pid={tid}&category_id={cateId}&type={cls}&area={area}&year={year}&sort={sort_val}&page={pg}"
            res = self.fetch(f"{self.host}{path}", headers=self.headers, verify=False).json()
            videos.extend(self.arr2vods(res.get("data", [])))
        return {"list": videos, "page": pg}

    def searchContent(self, key, quick, pg='1'):
        try:
            res = self.fetch(f'{self.host}/api/v2/search/videoV2?key={key}&page={pg}&pageSize=20', headers=self.headers, verify=False).json()
            videos = self.arr2vods(res.get("data", []))
            total = res.get("total", 0)
        except Exception:
            videos = []
            total = 0
        return {"list": videos, "page": pg, "total": total}

    def detailContent(self, ids):
        if not ids:
            return {"list": []}
        tid, vid = ids[0].split('@', 1)
        show, play_urls = [], []
        try:
            if tid == "67":
                res = self.fetch(f"{self.host}/api/detail?token=&vid={vid}", headers=self.headers, verify=False).json()
                data = res.get("data", {})
                line_name = ""
                for pl in data.get("playlist", []):
                    if not line_name:
                        line_name = pl.get("source_config_name", "线路1")
                    play_urls.append(f"{pl.get('title','')}${pl.get('url','noUrl')}")
                if not line_name:
                    line_name = "荐片"
                show.append(line_name)
                img_url = data.get("thumbnail", data.get("cover_image", data.get("path", "")))
                video = {
                    "vod_id": ids[0],
                    "vod_name": data.get("title", ""),
                    "vod_pic": self.pic(img_url),
                    "vod_remarks": data.get("mask", ""),
                    "vod_year": data.get("year", "1000"),
                    "type_name": ",".join([x.get("name","") for x in data.get("types", [])]) or "类型",
                    "vod_actor": ",".join([x.get("name","") for x in data.get("actors", [])]) or "未知",
                    "vod_director": ",".join([x.get("name","") for x in data.get("directors", [])]) or "未知",
                    "vod_area": ",".join([x.get("title","") for x in data.get("category", [])]) or "地区",
                    "vod_content": data.get("description", data.get("title", "暂无简介")),
                    "vod_play_from": "$$$".join(show),
                    "vod_play_url": "#".join(play_urls)
                }
            else:
                res = self.fetch(f"{self.host}/api/video/detailv2?id={vid}", headers=self.headers, verify=False).json()
                data = res.get("data", {})
                for src in data.get("source_list_source", []):
                    urls = []
                    for idx, item in enumerate(src.get("source_list", [])):
                        name = item.get("source_name", item.get("weight", f"{idx+1}集"))
                        urls.append(f"{name}${item.get('url','noUrl')}")
                    play_urls.append("#".join(urls))
                    show.append(src.get("name", f"线路{len(show)+1}"))
                img_url = data.get("thumbnail", data.get("cover_image", data.get("path", "")))
                video = {
                    "vod_id": ids[0],
                    "vod_name": data.get("title", ""),
                    "vod_pic": self.pic(img_url),
                    "vod_remarks": data.get("mask", ""),
                    "vod_year": data.get("year", "1000"),
                    "type_name": ",".join([x.get("name","") for x in data.get("types", [])]) or "类型",
                    "vod_actor": ",".join([x.get("name","") for x in data.get("actors", [])]) or "未知",
                    "vod_director": ",".join([x.get("name","") for x in data.get("directors", [])]) or "未知",
                    "vod_area": ",".join([x.get("title","") for x in data.get("category", [])]) or "地区",
                    "vod_content": data.get("description", "暂无简介"),
                    "vod_play_from": "$$$".join(show),
                    "vod_play_url": "$$$".join(play_urls)
                }
            return {"list": [video]}
        except Exception:
            return {"list": []}

    def playerContent(self, flag, url, vip_flags):
        headers = {
            "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 15)",
            "Connection": "Keep-Alive",
            "Accept-Encoding": "gzip",
            "token": ""
        }
        return {"parse": 0, "jx": 0, "url": url, "header": headers}

    def arr2vods(self, arr, tid=None):
        videos = []
        if not isinstance(arr, list):
            return videos
        for item in arr:
            img_url = item.get("thumbnail", item.get("cover_image", item.get("path", "")))
            cid = tid or item.get("top_category", {}).get("id") or "Unknown"
            videos.append({
                "vod_id": f"{cid}@{item.get('id','')}",
                "vod_name": item.get("title", ""),
                "vod_pic": self.pic(img_url),
                "vod_remarks": item.get("mask", ""),
                "vod_year": item.get("score", ""),
            })
        return videos

    def pic(self, url):
        if not isinstance(url, str) or not url.strip():
            return ""
        if not url.startswith(("http://", "https://")):
            domain = self.pic_domain or (self.pic_domains[0] if self.pic_domains else "")
            return domain + url
        return url

    def homeVideoContent(self):
        pass
    def localProxy(self, params):
        pass
    def isVideoFormat(self, url):
        pass
    def manualVideoCheck(self):
        pass
    def getName(self):
        pass
