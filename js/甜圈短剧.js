
var rule = {
    类型: '影视',
    title: '甜圈短剧[短]',
    host: 'https://mov.cenguigui.cn',
    url: '/duanju/api.php?classname=fyclass&offset=fypage',
    searchUrl: '/duanju/api.php?name=**&page=fypage',
    searchable: 2,
    quickSearch: 0,
    filterable: 0,
    search_match: true, //精准搜索
    headers: {
        'User-Agent': 'MOBILE_UA',
        'Referer': HOST +'/'
    },
    timeout: 5000,    
    class_name: '新剧&逆袭&霸总&现代言情&打脸虐渣&豪门恩怨&神豪&马甲&都市日常&小人物&女性成长&大女主&穿越&都市修仙&亲情&古装&重生&闪婚&赘婿逆袭&虐恋&追妻&天下无敌&家庭伦理&萌宝&古风权谋&职场&奇幻脑洞&异能&古风言情&传承觉醒&现言甜宠&奇幻爱情&乡村&历史古代&王妃&高手下山&娱乐圈&强强联合&破镜重圆&暗恋成真& 民国&欢喜冤家&系统&真假千金&校园&穿书&女帝&团宠&年代爱情&玄幻仙侠&青梅竹马&悬疑推理&皇后&替身&大叔&喜剧&剧情',    
    class_url: '新剧&逆袭&霸总&现代言情&打脸虐渣&豪门恩怨&神豪&马甲&都市日常&小人物&女性成长&大女主&穿越&都市修仙&亲情&古装&重生&闪婚&赘婿逆袭&虐恋&追妻&天下无敌&家庭伦理&萌宝&古风权谋&职场&奇幻脑洞&异能&古风言情&传承觉醒&现言甜宠&奇幻爱情&乡村&历史古代&王妃&高手下山&娱乐圈&强强联合&破镜重圆&暗恋成真&民国&欢喜冤家&系统&真假千金&校园&穿书&女帝&团宠&年代爱情&玄幻仙侠&青梅竹马&悬疑推理&皇后&替身&大叔&喜剧&剧情',    
    play_parse: true,
    double: true,
    lazy: $js.toString(() => {
        input = {
            parse: 0,
            url: HOST + '/duanju/api.php?video_id=' + input + '&type=mp4',
            jx: 0
        };
    }),        
    推荐: $js.toString(() => {
        let url = HOST + '/duanju/api.php?classname=推荐榜&offset=0';
        let res = request(url, {headers: rule.headers});
        let data = JSON.parse(res).data;
        VODS = [];
        data.forEach(item => {
            VODS.push({
                vod_id: item.book_id,
                vod_name: item.title,
                vod_pic: item.cover,
                vod_remarks: `${item.sub_title}|${item.episode_cnt}集`
            });
        });
    }),    
    一级: $js.toString(() => {
        let res = request(input, {headers: rule.headers});
        let data = JSON.parse(res).data;
        VODS = [];
        data.forEach(item => {
            VODS.push({
                vod_id: item.book_id,
                vod_name: item.title,
                vod_pic: item.cover,
                vod_remarks: `${item.sub_title}|${item.episode_cnt}集`
            });
        });
    }),    
    二级: $js.toString(() => {
        let book_id = orId;
        let url = HOST + '/duanju/api.php?book_id=' + book_id;
        let res = request(url, {headers: rule.headers});
        let item = JSON.parse(res);
        let playUrls = item.data.map(ep => `${ep.title}$${ep.video_id}`);
        VOD = {
            vod_id: book_id,
            vod_name: item.book_name || item.title,
            type_name: item.category,
            vod_pic: item.book_pic || item.cover,
            vod_content: item.desc,
            vod_remarks: item.duration,
            vod_year: item.time,
            //vod_actor: item.author,
            vod_play_from: '甜圈短剧',
            vod_play_url: playUrls.join("#")
        };
    }),    
    搜索: $js.toString(() => {
        let d = [];
        let html =  request(input, {headers: rule.headers });
        let data = JSON.parse(html).data;
        if (rule.search_match) {
            data = data.filter(item =>
                item.title &&
                new RegExp(KEY, "i").test(item.title)
            );
        }
        data.forEach((it) => {
            d.push({
                title: it.title,
                img: it.cover,
                year: it.author,
                desc: it.type,
                url: it.book_id
            });
        });
         setResult(d);
    }),
}
