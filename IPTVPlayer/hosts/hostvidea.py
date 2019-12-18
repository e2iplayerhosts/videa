# -*- coding: utf-8 -*-
###################################################
# 2019-12-18 by Alec - Videa
###################################################
HOST_VERSION = "1.1"
###################################################
# LOCAL import
###################################################
from Plugins.Extensions.IPTVPlayer.components.iptvplayerinit import TranslateTXT as _, SetIPTVPlayerLastHostError
from Plugins.Extensions.IPTVPlayer.components.ihost import CHostBase, CBaseHostClass, CDisplayListItem, RetHost, CUrlItem
from Plugins.Extensions.IPTVPlayer.tools.iptvtools import printDBG, GetLogoDir, GetIPTVPlayerVerstion, MergeDicts
from Plugins.Extensions.IPTVPlayer.tools.iptvtypes import strwithmeta
from Plugins.Extensions.IPTVPlayer.libs.urlparserhelper import getDirectM3U8Playlist, getF4MLinksWithMeta, getMPDLinksWithMeta
from Plugins.Extensions.IPTVPlayer.libs.urlparser import urlparser
from Plugins.Extensions.IPTVPlayer.libs import ph
###################################################

###################################################
# FOREIGN import
###################################################
from Components.config import config, ConfigText, ConfigYesNo, ConfigDirectory, getConfigListEntry
from os.path import normpath
import urlparse
import os
import re
import urllib
import random
import datetime
import time
import zlib
import cookielib
import base64
import codecs
import traceback
try:
    import subprocess
    FOUND_SUB = True
except Exception:
    FOUND_SUB = False
from Tools.Directories import resolveFilename, fileExists, SCOPE_PLUGINS
from Screens.MessageBox import MessageBox
from hashlib import sha1
###################################################

###################################################
# Config options for HOST
###################################################
config.plugins.iptvplayer.videa_id = ConfigYesNo(default = False)
config.plugins.iptvplayer.boxtipus = ConfigText(default = "", fixed_size = False)
config.plugins.iptvplayer.boxrendszer = ConfigText(default = "", fixed_size = False)

def GetConfigList():
    optionList = []
    optionList.append(getConfigListEntry("id:", config.plugins.iptvplayer.videa_id))
    return optionList
###################################################

def gettytul():
    return 'Videa'

class videa(CBaseHostClass):

    def __init__(self):
        CBaseHostClass.__init__(self, {'history':'videa', 'cookie':'videa.cookie'})
        self.USER_AGENT = 'User-Agent=Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.0'
        self.HEADER = self.cm.getDefaultHeader()
        self.DEFAULT_ICON_URL = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1S/LTElNjM/JT8/XyypIBwBrnxCf'))
        self.MAIN_URL = zlib.decompress(base64.b64decode('eJzLKCkpKLbS1y/LTElN1MsoBQAy9gXg'))
        self.vmk = self.MAIN_URL + zlib.decompress(base64.b64decode('eJzTz04sSU3PL8pMzAYAGM8EUg=='))
        self.vmcs = self.MAIN_URL + zlib.decompress(base64.b64decode('eJzTTy5OLMkvykvMBgAUvAP2'))
        self.vmkrs = self.MAIN_URL + zlib.decompress(base64.b64decode('eJzTL8tMSc2Pz04tSi1OLQYAKFYFmA=='))
        self.vivn = GetIPTVPlayerVerstion()
        self.porv = self.gits()
        self.pbtp = '-'
        self.btps = config.plugins.iptvplayer.boxtipus.value
        self.brdr = config.plugins.iptvplayer.boxrendszer.value
        self.aid = config.plugins.iptvplayer.videa_id.value
        self.aid_ki = ''
        self.vszkzrs = []
        self.defaultParams = {'header':self.HEADER, 'use_cookie': False, 'load_cookie': False, 'save_cookie': False, 'cookiefile': self.COOKIE_FILE}
        
    def _uriIsValid(self, url):
        return '://' in url
        
    def getFullIconUrl(self, url):
        url = url.replace('&amp;', '&')
        return CBaseHostClass.getFullIconUrl(self, url)
        
    def getPage(self, baseUrl, addParams = {}, post_data = None):
        if addParams == {}:
            addParams = dict(self.defaultParams)
        
        def _getFullUrl(url):
            if self.cm.isValidUrl(url):
                return url
            else:
                return urlparse.urljoin(baseUrl, url)
            
        addParams['cloudflare_params'] = {'domain':self.up.getDomain(baseUrl), 'cookie_file':self.COOKIE_FILE, 'User-Agent':self.USER_AGENT, 'full_url_handle':_getFullUrl}
        sts, data = self.cm.getPageCFProtection(baseUrl, addParams, post_data)
        return sts, data
        
    def listMainMenu(self, cItem):
        try:
            if not self.ebbtit(): return
            if self.btps != '' and self.brdr != '': self.pbtp = self.btps.strip() + ' - ' + self.brdr.strip()            
            tab_kat = 'videa_kategoriak'
            desc_kat = self.getdvdsz(tab_kat, 'Videa kategóriáinak megjelenítése...')
            tab_csat = 'videa_csatornak'
            desc_csat = self.getdvdsz(tab_csat, 'Videa csatornáinak megjelenítése...')
            tab_ajanlott = 'videa_ajanlott'
            desc_ajanlott = self.getdvdsz(tab_ajanlott, 'Ajánlott, nézett tartalmak megjelenítése...')
            tab_keresett = 'videa_keresett_tartalom'
            desc_keresett = self.getdvdsz(tab_keresett, 'Keresett tartalmak megjelenítése...')
            tab_search = 'videa_kereses'
            desc_search = self.getdvdsz(tab_search, 'Keresés...')
            tab_search_hist = 'videa_kereses_elozmeny'
            desc_search_hist = self.getdvdsz(tab_search_hist, 'Keresés az előzmények között...')
            MAIN_CAT_TAB = [{'category':'list_main', 'title': 'Kategóriák', 'tab_id':tab_kat, 'desc':desc_kat},
                            {'category':'list_main', 'title': 'Csatornák', 'tab_id':tab_csat, 'desc':desc_csat},
                            {'category':'list_main', 'title': 'Ajánlott, nézett tartalmak', 'tab_id':tab_ajanlott, 'desc':desc_ajanlott},
                            {'category':'list_main', 'title': 'Keresett tartalmak', 'tab_id':tab_keresett, 'desc':desc_keresett},
                            {'category':'search', 'title': _('Search'), 'search_item':True, 'tab_id':tab_search, 'desc':desc_search},
                            {'category':'search_history', 'title': _('Search history'), 'tab_id':tab_search_hist, 'desc':desc_search_hist} 
                           ]
            self.listsTab(MAIN_CAT_TAB, {'name':'category'})
            vtb = self.malvadnav(cItem, '7', '12', '0', '14')
            if len(vtb) > 0:
                for item in vtb:
                    item['category'] = 'list_third'
                    self.addVideo(item)
        except Exception:
            return
            
    def listMainItems(self, cItem):
        try:
            self.vszkzrs = self.malvadkiszrz()
            tabID = cItem.get('tab_id', '')
            if tabID == 'videa_kategoriak':
                self.Vdktgrk(cItem, tabID)
            elif tabID == 'videa_csatornak':
                self.Vdcstrnk(cItem, tabID)
            elif tabID == 'videa_ajanlott':
                self.Vdajnzttt(cItem, tabID)
            elif tabID == 'videa_keresett_tartalom':
                self.Vdakstmk({'name':'history', 'category': 'search', 'tab_id':''}, 'desc', _("Type: "), tabID)
            else:
                return
        except Exception:
            return
            
    def Vdktgrk(self, cItem, tabID):
        mlt = []
        try:
            self.susn('2', '12', tabID)
            url_ere = self.MAIN_URL
            sts, data = self.getPage(url_ere)
            if not sts: return
            if len(data) == 0: return
            data = self.cm.ph.getDataBeetwenMarkers(data, 'id="menu-categories"', '</ul>')[1]
            if len(data) == 0: return
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
            if len(data) == 0: return
            for item in data:
                url = self.cm.ph.getSearchGroups(item, 'href=[\'"]([^"^\']+?)[\'"]')[0]
                if url.startswith('/'):
                    url = url_ere + url
                if not self.cm.isValidUrl(url):
                    continue
                title = self.cleanHtmlStr(item).capitalize()
                desc = self.getdvdsz(url, '"' + title + '"  kategória videóinak megjelenítése...')
                icon = ''
                params = MergeDicts(cItem, {'good_for_fav': False, 'category':'list_second', 'title':title, 'url':url, 'icon':icon, 'desc':desc, 'tab_id':tabID})
                mlt.append(params)
            if len(mlt) > 0:
                random.shuffle(mlt)
                for ipv in mlt:
                    self.addDir(ipv)
        except Exception:
            return
            
    def Vdcstrnk(self, cItem, tabID):
        mlt = []
        try:
            self.susn('2', '12', tabID)
            url_ere = self.MAIN_URL
            sts, data = self.getPage(url_ere)
            if not sts: return
            if len(data) == 0: return
            data = self.cm.ph.getDataBeetwenMarkers(data, 'id="menu-channels"', '</ul>')[1]
            if len(data) == 0: return
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<li', '</li>')
            if len(data) == 0: return
            for item in data:
                url = self.cm.ph.getSearchGroups(item, 'href=[\'"]([^"^\']+?)[\'"]')[0]
                if url.startswith('/'):
                    url = url_ere + url
                if not self.cm.isValidUrl(url):
                    continue
                title = self.cleanHtmlStr(item).capitalize()
                desc = self.getdvdsz(url, '"' + title + '"  csatorna videóinak megjelenítése...')
                icon = ''
                params = MergeDicts(cItem, {'good_for_fav': False, 'category':'list_second', 'title':title, 'url':url, 'icon':icon, 'desc':desc, 'tab_id':tabID})
                mlt.append(params)
            if len(mlt) > 0:
                random.shuffle(mlt)
                for ipv in mlt:
                    self.addDir(ipv)
        except Exception:
            return
            
    def Vdajnzttt(self, cItem, tabID):
        try:
            self.susn('2', '12', tabID)
            tab_ams = 'videa_ajnlt_musor'
            desc_ams = self.getdvdsz(tab_ams, 'Ajánlott, nézett tartalmak megjelenítése műsorok szerint...')
            tab_adt = 'videa_ajnlt_datum'
            desc_adt = self.getdvdsz(tab_adt, 'Ajánlott, nézett tartalmak megjelenítése dátum szerint...')
            tab_anzt = 'videa_ajnlt_nezettseg'
            desc_anzt = self.getdvdsz(tab_anzt, 'Ajánlott, nézett tartalmak megjelenítése nézettség szerint...')
            A_CAT_TAB = [{'category':'list_third', 'title': 'Dátum szerint', 'tab_id':tab_adt, 'desc':desc_adt},
                         {'category':'list_third', 'title': 'Műsorok szerint', 'tab_id':tab_ams, 'desc':desc_ams},
                         {'category':'list_third', 'title': 'Nézettség szerint', 'tab_id':tab_anzt, 'desc':desc_anzt} 
                        ]
            self.listsTab(A_CAT_TAB, cItem)
        except Exception:
            return
            
    def listSecondItems(self, cItem):
        try:
            tabID = cItem.get('tab_id', '')
            if tabID == 'videa_kategoriak':
                url = cItem['url']
                self.susn('2', '12', url)
                VK_CAT_TAB = [{'category':'list_items', 'title': 'Feltöltés ideje szerint', 'url':url+'?sort=0&interval=0&category=0&usergroup=0&page=1', 'desc':''},
                              {'category':'list_items', 'title': 'Nézettség szerint', 'url':url+'?sort=1&interval=0&category=0&usergroup=0&page=1', 'desc':''},
                              {'category':'list_items', 'title': 'Név szerint', 'url':url+'?sort=3&interval=0&category=0&usergroup=0&page=1', 'desc':''}
                             ]
                self.listsTab(VK_CAT_TAB, cItem)
            elif tabID == 'videa_csatornak':
                url = cItem['url']
                self.susn('2', '12', url)
                VCS_CAT_TAB = [{'category':'list_items', 'title': 'Feltöltés ideje szerint', 'url':url+'?sort=0&interval=0&category=0&usergroup=0&page=1', 'desc':''},
                               {'category':'list_items', 'title': 'Nézettség szerint', 'url':url+'?sort=1&interval=0&category=0&usergroup=0&page=1', 'desc':''},
                               {'category':'list_items', 'title': 'Név szerint', 'url':url+'?sort=3&interval=0&category=0&usergroup=0&page=1', 'desc':''}
                              ]
                self.listsTab(VCS_CAT_TAB, cItem)
            else:
                return
        except Exception:
            return
            
    def listThirdItems(self, cItem):
        try:
            tabID = cItem.get('tab_id', '')
            if tabID == 'videa_ajnlt_musor':
                self.Vajnltmsr(cItem)
            elif tabID == 'videa_ajnlt_datum':
                self.Vajnltdtm(cItem)
            elif tabID == 'videa_ajnlt_nezettseg':
                self.Vajnltnztsg(cItem)
            else:
                return
        except Exception:
            return
            
    def Vajnltmsr(self,cItem):
        try:
            self.susn('2', '12', 'videa_ajnlt_musor')
            vtb = self.malvadnav(cItem, '3', '12', '0')
            if len(vtb) > 0:
                for item in vtb:
                    self.addVideo(item)
        except Exception:
            return
            
    def Vajnltdtm(self,cItem):
        vtb = []
        try:
            self.susn('2', '12', 'videa_ajnlt_datum')
            vtb = self.malvadnav(cItem, '4', '12', '0')
            if len(vtb) > 0:
                for item in vtb:
                    self.addVideo(item)
        except Exception:
            return
            
    def Vajnltnztsg(self,cItem):
        try:
            self.susn('2', '12', 'videa_ajnlt_nezettseg')
            vtb = self.malvadnav(cItem, '5', '12', '0')
            if len(vtb) > 0:
                for item in vtb:
                    self.addVideo(item)
        except Exception:
            return
            
    def listItems(self, cItem):
        try:
            url_ere = cItem['url']
            page = cItem.get('page', 1)
            if page > 0 and 'page=' in url_ere:
                idx1 = url_ere.rfind('page=')
                if -1 < idx1:
                    url_ere = url_ere[:idx1].strip()
                    url_ere = url_ere + 'page=' + str(page)
            sts, data = self.getPage(url_ere)
            if not sts: return
            if len(data) == 0: return
            nextPage = self.cm.ph.getDataBeetwenMarkers(data, '<i class="vicon-kisnyil-bal">', '<i class="vicon-kisnyil-jobb">')[1]
            if '' != self.cm.ph.getSearchGroups(nextPage, 'page=(%s)[^0-9]' % (page+1))[0]: nextPage = True
            else: nextPage = False
            #data = self.cm.ph.getDataBeetwenMarkers(data, '<div class="list-menu-row-order-links">', '<div class="main-menu">')[1]
            #if len(data) == 0: return
            #data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="col-xxs-12 col-xs-6 col-sm-4 col-lg-2 col-video"', '<i class="vicon-szem video-stat-footer">')
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="col-xxs-12 col-xs-6 col-sm-4 col-lg-2 col-video"', '</span></div>')
            if len(data) == 0: return
            for item in data:
                temp_url = self.cm.ph.getDataBeetwenMarkers(item, '<div class="panel-video-title">', '</div>', False)[1]
                url = self.cm.ph.getSearchGroups(temp_url, 'href=[\'"]([^"^\']+?)[\'"]')[0]
                if not self.cm.isValidUrl(url): continue
                temp_icon = self.cm.ph.getDataBeetwenMarkers(item, ' <a class="video-link', '</a>')[1]
                icon = self.cm.ph.getSearchGroups(temp_icon, '''src=['"]([^"^']+?)['"]''')[0]
                if icon == '':
                    icon = self.DEFAULT_ICON_URL
                else:
                    if icon.startswith('/'): icon = self.MAIN_URL + icon
                vszrz = self.cm.ph.getDataBeetwenMarkers(item, '<div class="panel-video-text"', '</a>')[1]
                if len(self.vszkzrs) > 0:
                    if self.check_string(vszrz,self.vszkzrs): continue
                vhz = self.cm.ph.getDataBeetwenMarkers(item, '<span class="label label-black video-length">', '</span>', False)[1]
                vmsg = self.cm.ph.getDataBeetwenMarkers(item, '<span class="video-hd">', '</span>', False)[1]
                if vmsg != '':
                    vmsg = '  |  ' + vmsg
                title = self.cleanHtmlStr(temp_url).strip()
                if title == '': continue 
                ftlv = self.cleanHtmlStr(self.cm.ph.getDataBeetwenMarkers(item, '<i class="vicon-ora"></i>', '</span>', False)[1]).strip()
                desc = 'Feltöltve: ' + ftlv + '  |  Időtartam: ' + vhz + vmsg + '\n\nCím: ' + title
                params = MergeDicts(cItem, {'good_for_fav': False, 'title':title, 'url':url, 'icon':icon, 'desc':desc, 'tps':'0'})
                self.addVideo(params)
            if nextPage:
                params = dict(cItem)
                params.update({'title':_("Next page"), 'page':page+1, 'desc':'Nyugi...\nVan még további tartalom, lapozz tovább!!!'})
                self.addDir(params)
        except Exception:
            return
            
    def getLinksForVideo(self, cItem):
        try:
            urlTab = []
            url = cItem['url']
            baseUrl = strwithmeta(url)
            HTTP_HEADER = self.cm.getDefaultHeader(browser='chrome')
            referer = baseUrl.meta.get('Referer')
            if referer: HTTP_HEADER['Referer'] = referer
            urlParams = {'header':HTTP_HEADER}
            sts, data = self.cm.getPage(baseUrl, urlParams)
            if not sts: return []
            if data == '': return []
            cUrl = self.cm.meta['url']
            f = ph.find(data, zlib.decompress(base64.b64decode('eJwryEmsTC2yBwALugLN')), '&', flags=0)[1]
            if not f: f = cUrl.split(zlib.decompress(base64.b64decode('eJwryEmsTC2yBwALugLN')), 1)[-1].rsplit('&', 1)[0]
            if not f: f = ph.find(data, zlib.decompress(base64.b64decode('eJwryEmsTC2yBwALugLN')), '&', flags=0)[1]
            if not f: return []
            url = zlib.decompress(base64.b64decode('eJwVylsKgCAQBdDd+NljAdJSZMJrRqbDOEQh7r36PZzx2j2IEz0Qt0HdfaaBIy9t6qYqidrJINOaUDNxjeWH72soclqPemhhIwgQgdg29xc2Sx/I')).format(f, urllib.quote(baseUrl))
            sts, data = self.cm.getPage(self.cm.getFullUrl(url, cUrl))
            if not sts: return []
            if data == '': return []
            meta = {'Referer':cUrl, 'Origin':urlparser.getDomain(baseUrl, False)[:-1], 'User-Agent':HTTP_HEADER['User-Agent']}
            hlsMeta = MergeDicts(meta, {'iptv_proto':'m3u8'})
            data = ph.find(data, ('<video_sources', '>'), '</video_sources>', flags=0)[1]
            if data == '': return []
            data = ph.findall(data, ('<video_source', '>'), '</video_source>')
            if data == '': return []
            for item in data:
                url = self.cm.getFullUrl(ph.clean_html(item), cUrl)
                if not url: continue
                if 'video/mp4' in item:
                    width  = ph.getattr(item, 'width')
                    height = ph.getattr(item, 'height')
                    name   = ph.getattr(item, 'name')
                    url    = urlparser.decorateUrl(url, meta)
                    urlTab.append({'name':'{0} - {1}x{2}'.format(name, width, height), 'url':url})
                elif 'mpegurl' in item:
                    url = urlparser.decorateUrl(url, hlsMeta)
                    tmpTab = getDirectM3U8Playlist(url, checkExt=False, checkContent=True)
                    urlTab.extend(tmpTab)
            urlTab.reverse()
            if cItem['category'] != 'list_third':
                self.susmrgts('2', '12', cItem['tps'], cItem['url'], cItem['title'], cItem['icon'], cItem['desc'], 'mnez')
            return urlTab
        except Exception:
            return []
    
    def cpve(self, cfpv=''):
        vissza = False
        try:
            if cfpv != '':
                mk = cfpv
                if mk != '':
                    vissza = True
        except Exception:
            return False
        return vissza
        
    def check_string(self, string, substring_list):
        for substring in substring_list:
            if substring in string:
                return True
        return False
        
    def getdvdsz(self, pu='', psz=''):
        bv = ''
        if pu != '' and psz != '':
            n_atnav = self.malvadst('1', '12', pu)
            if n_atnav != '' and self.aid:
                if pu == 'videa_kategoriak':
                    self.aid_ki = 'ID: ' + n_atnav + '  |  Videa  v' + HOST_VERSION + '\n'
                else:
                    self.aid_ki = 'ID: ' + n_atnav + '\n'
            else:
                if pu == 'videa_kategoriak':
                    self.aid_ki = 'Videa  v' + HOST_VERSION + '\n'
                else:
                    self.aid_ki = ''
            bv = self.aid_ki + psz
        return bv
        
    def malvadst(self, i_md='', i_hgk='', i_mpu=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUL04sSdQvS8wD0ilJegUZBQD8FROZ'))
        pstd = {'md':i_md, 'hgk':i_hgk, 'mpu':i_mpu}
        t_s = ''
        temp_vn = ''
        temp_vni = ''
        try:
            if i_md != '' and i_hgk != '' and i_mpu != '':
                sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
                if not sts: return t_s
                if len(data) == 0: return t_s
                data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="div_a_div', '</div>')[1]
                if len(data) == 0: return t_s
                data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<input', '/>')
                if len(data) == 0: return t_s
                for item in data:
                    t_i = self.cm.ph.getSearchGroups(item, 'id=[\'"]([^"^\']+?)[\'"]')[0]
                    if t_i == 'vn':
                        temp_vn = self.cm.ph.getSearchGroups(item, 'value=[\'"]([^"^\']+?)[\'"]')[0]
                    elif t_i == 'vni':
                        temp_vni = self.cm.ph.getSearchGroups(item, 'value=[\'"]([^"^\']+?)[\'"]')[0]
                if temp_vn != '':
                    t_s = temp_vn
            return t_s
        except Exception:
            return t_s
            
    def malvadnav(self, cItem, i_md='', i_hgk='', i_mptip='', i_mpdb=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzy0tSQQTxYklKUl6BRkFABGoFBk='))
        t_s = []
        try:
            if i_md != '' and i_hgk != '' and i_mptip != '':
                if i_hgk != '': i_hgk = base64.b64encode(i_hgk).replace('\n', '').strip()
                if i_mptip != '': i_mptip = base64.b64encode(i_mptip).replace('\n', '').strip()
                if i_mpdb != '': i_mpdb = base64.b64encode(i_mpdb).replace('\n', '').strip()
                pstd = {'md':i_md, 'hgk':i_hgk, 'mptip':i_mptip, 'mpdb':i_mpdb}
                sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
                if not sts: return t_s
                if len(data) == 0: return t_s
                data = self.cm.ph.getDataBeetwenMarkers(data, '<div id="div_a1_div"', '<div id="div_a2_div"')[1]
                if len(data) == 0: return t_s
                data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div class="d_sor_d"', '</div>')
                if len(data) == 0: return t_s
                for temp_item in data:
                    temp_data = self.cm.ph.getAllItemsBeetwenMarkers(temp_item, '<span', '</span>')
                    if len(temp_data) == 0: return t_s
                    for item in temp_data:
                        t_vp = self.cm.ph.getSearchGroups(item, 'class=[\'"]([^"^\']+?)[\'"]')[0]
                        if t_vp == 'c_sor_u':
                            temp_u = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_u">', '</span>', False)[1]
                            if temp_u != '': temp_u = base64.b64decode(temp_u)
                        if t_vp == 'c_sor_t':
                            temp_t = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_t">', '</span>', False)[1]
                            if temp_t != '': temp_t = base64.b64decode(temp_t)
                        if t_vp == 'c_sor_i':
                            temp_i = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_i">', '</span>', False)[1]
                            if temp_i != '': temp_i = base64.b64decode(temp_i)
                        if t_vp == 'c_sor_l':
                            temp_l = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_l">', '</span>', False)[1]
                            if temp_l != '': temp_l = base64.b64decode(temp_l)
                        if t_vp == 'c_sor_n':
                            temp_n = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_n">', '</span>', False)[1]
                            if temp_n != '': temp_n = base64.b64decode(temp_n)
                        if t_vp == 'c_sor_tip':
                            temp_tp = self.cm.ph.getDataBeetwenMarkers(item, '<span class="c_sor_tip">', '</span>', False)[1]
                            if temp_tp != '': temp_tp = base64.b64decode(temp_tp)
                    if temp_u == '' and temp_t =='': continue
                    if temp_n == '': temp_n = '1'
                    params = MergeDicts(cItem, {'good_for_fav': False, 'url':temp_u, 'title':temp_t, 'icon':temp_i, 'desc':temp_l, 'nztsg':temp_n, 'tps':temp_tp})
                    t_s.append(params)       
            return t_s
        except Exception:
            return []
        
    def susmrgts(self, i_md='', i_hgk='', i_mptip='', i_mpu='', i_mpt='', i_mpi='', i_mpdl='', i_mpnzs=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzy0tSQQTxYklKUl6BRkFABGoFBk='))
        try:
            if i_hgk != '': i_hgk = base64.b64encode(i_hgk).replace('\n', '').strip()
            if i_mptip != '': i_mptip = base64.b64encode(i_mptip).replace('\n', '').strip()
            if i_mpu != '': i_mpu = base64.b64encode(i_mpu).replace('\n', '').strip()
            if i_mpt != '': i_mpt = base64.b64encode(i_mpt).replace('\n', '').strip()
            if i_mpi == '':
                i_mpi = base64.b64encode('-')
            else:
                i_mpi = base64.b64encode(i_mpi).replace('\n', '').strip()
            if i_mpdl == '':
                i_mpdl = base64.b64encode('-')
            else:
                i_mpdl = base64.b64encode(i_mpdl).replace('\n', '').strip()
            if i_mpnzs != '': i_mpnzs = base64.b64encode(i_mpnzs).replace('\n', '').strip()
            pstd = {'md':i_md, 'hgk':i_hgk, 'mptip':i_mptip, 'mpu':i_mpu, 'mpt':i_mpt, 'mpi':i_mpi, 'mpdl':i_mpdl, 'mpnzs':i_mpnzs}
            if i_md != '' and i_hgk != '' and i_mptip != '' and i_mpu != '':
                sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
            return
        except Exception:
            return
            
    def suskrbt(self, i_md='', i_hgk='', i_mpsz=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzwbywERxYklKkl5BRgEAD/4T/Q=='))
        try:
            if i_mpsz != '' and len(i_mpsz) > 1:
                if len(i_mpsz) > 80:
                    i_mpsz = i_mpsz[:78]
                i_mpsz = base64.b64encode(i_mpsz).replace('\n', '').strip()
                if i_hgk != '':
                    i_hgk = base64.b64encode(i_hgk).replace('\n', '').strip()
                    pstd = {'md':i_md, 'hgk':i_hgk, 'mpsz':i_mpsz}
                    if i_md != '' and i_hgk != '' and i_mpsz != '':
                        sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
            return
        except Exception:
            return
            
    def susn(self, i_md='', i_hgk='', i_mpu=''):
        uhe = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUL04sSdQvS8wD0ilJegUZBQD8FROZ'))
        pstd = {'md':i_md, 'hgk':i_hgk, 'mpu':i_mpu, 'hv':self.vivn, 'orv':self.porv, 'bts':self.pbtp}
        try:
            if i_md != '' and i_hgk != '' and i_mpu != '':
                sts, data = self.cm.getPage(uhe, self.defaultParams, pstd)
            return
        except Exception:
            return
            
    def malvadkiszrz(self):
        bv = []
        ukszrz = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzy0tSQQTxYklKUnZmXoFGQUAO30U7Q=='))
        try:
            sts, data = self.cm.getPage(ukszrz)
            if not sts: return []
            if len(data) == 0: return []
            data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div>', '</div>', False)
            if len(data) == 0: return []
            for item in data:
                bv.append(item)
            return bv
        except Exception:
            return []
            
    def malvadkrttmk(self, i_md='', i_hgk=''):
        bv = []
        ukszrz = zlib.decompress(base64.b64decode('eJzLKCkpsNLXLy8v10vLTK9MzclNrSpJLUkt1sso1c9IzanUzwbywERxYklKkl5BRgEAD/4T/Q=='))
        try:
            if i_md != '' and i_hgk != '':
                i_hgk = base64.b64encode(i_hgk).replace('\n', '').strip()
                pstd = {'md':i_md, 'hgk':i_hgk}
                sts, data = self.cm.getPage(ukszrz, self.defaultParams, pstd)
                if not sts: return []
                if len(data) == 0: return []
                data = self.cm.ph.getAllItemsBeetwenMarkers(data, '<div>', '</div>', False)
                if len(data) == 0: return []
                for item in data:
                    if item != '':
                        bv.append(base64.b64decode(item))
            return bv
        except Exception:
            return []
            
    def gits(self):
        bv = '-'
        tt = []
        try:
            if fileExists(zlib.decompress(base64.b64decode('eJzTTy1J1s8sLi5NBQATXQPE'))):
                fr = open(zlib.decompress(base64.b64decode('eJzTTy1J1s8sLi5NBQATXQPE')),'r')
                for ln in fr:
                    ln = ln.rstrip('\n')
                    if ln != '':
                        tt.append(ln)
                fr.close()
                if len(tt) == 1:
                    bv = tt[0].strip()[:-6].capitalize()
                if len(tt) == 2:
                    bv = tt[1].strip()[:-6].capitalize()
            return bv
        except:
            return '-'
        
    def ebbtit(self):
        try:
            if '' == self.btps.strip() or '' == self.brdr.strip():
                msg = 'A Set-top-Box típusát és a használt rendszer (image) nevét egyszer meg kell adni!\n\nA kompatibilitás és a megfelelő használat miatt kellenek ezek az adatok a programnak.\nKérlek, a helyes működéshez a valóságnak megfelelően írd be azokat.\n\nA "HU Telepítő" keretrendszerben tudod ezt megtenni.\n\nKilépek és megyek azt beállítani?'
                ret = self.sessionEx.waitForFinishOpen(MessageBox, msg, type=MessageBox.TYPE_YESNO, default=True)
                return False
            else:
                return True
        except Exception:
            return False
        
    def listSearchResult(self, cItem, searchPattern, searchType):
        try:
            self.suskrbt('2', '12', searchPattern)
            cItem = dict(cItem)
            cItem['url'] = self.vmkrs + '/' + urllib.quote_plus(searchPattern) + '?sort=0&interval=0&category=0&usergroup=0&page=1'
            self.listItems(cItem)
        except Exception:
            return
            
    def Vdakstmk(self, baseItem={'name': 'history', 'category': 'search'}, desc_key='plot', desc_base=(_("Type: ")), tabID='' ):
        if tabID != '':
            self.susn('2', '12', tabID)
            
        def _vdakstmk(data,lnp=50):
            ln = 0
            for histItem in data:
                plot = ''
                try:
                    ln += 1
                    if type(histItem) == type({}):
                        pattern = histItem.get('pattern', '')
                        search_type = histItem.get('type', '')
                        if '' != search_type: plot = desc_base + _(search_type)
                    else:
                        pattern = histItem
                        search_type = None
                    params = dict(baseItem)
                    params.update({'title': pattern, 'search_type': search_type,  desc_key: plot})
                    self.addDir(params)
                    if ln >= lnp:
                        break
                except Exception:
                    return
            
        try:
            list = self.malvadkrttmk('1','12')
            if len(list) > 0:
                _vdakstmk(list,2)
            if len(list) > 0:
                list = list[2:]
                random.shuffle(list)
                _vdakstmk(list,48)
        except Exception:
            return
    
    def handleService(self, index, refresh = 0, searchPattern = '', searchType = ''):
        try:
            CBaseHostClass.handleService(self, index, refresh, searchPattern, searchType)
            name = self.currItem.get("name", '')
            category = self.currItem.get("category", '')
            self.currList = []
            if name == None:
                self.listMainMenu( {'name':'category'} )
            elif category == 'list_main':
                self.listMainItems(self.currItem)
            elif category == 'list_second':
                self.listSecondItems(self.currItem)
            elif category == 'list_third':
                self.listThirdItems(self.currItem)
            elif category == 'list_items':
                self.listItems(self.currItem)
            elif category in ['search', 'search_next_page']:
                if self.currItem['tab_id'] == 'videa_kereses':
                    self.susn('2', '12', 'videa_kereses')
                cItem = dict(self.currItem)
                cItem.update({'search_item':False, 'name':'category'}) 
                self.listSearchResult(cItem, searchPattern, searchType)
            elif category == 'search_history':
                if self.currItem['tab_id'] == 'videa_kereses_elozmeny':
                    self.susn('2', '12', 'videa_kereses_elozmeny')
                self.listsHistory({'name':'history', 'category': 'search', 'tab_id':''}, 'desc', _("Type: "))
            else:
                return
            CBaseHostClass.endHandleService(self, index, refresh)
        except Exception:
            return

class IPTVHost(CHostBase):

    def __init__(self):
        CHostBase.__init__(self, videa(), True, [])
            
    def withArticleContent(self, cItem):
        if cItem['type'] != 'article':
            return False
        return True
