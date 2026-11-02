## 本 Fork：使用官方最新 Xray

基于 [yonggekkk/argosbx](https://github.com/yonggekkk/argosbx)，保留原作者署名及 GPL-3.0 许可证。
本 Fork 修改主脚本 `argosbx.sh` 的 Xray 下载、配置生成与升级兼容逻辑；Sing-box、Argo、协议选择及订阅参数保持原逻辑。

- 安装、`rep` 重建或 `upx` 时，从 `XTLS/Xray-core` 的 GitHub Latest Release 获取最新正式版，支持 amd64 / arm64；不是后台定时升级。
- 使用官方资产 SHA-256 校验，先下载、校验、执行配置检查，再替换内核。下载或配置检查失败时，`upx` 保留原内核和配置。
- 新配置使用 `streamSettings.sockopt.domainStrategy`、`dialerProxy`、`raw` 和 REALITY `target`；移除服务端无效的 `fingerprint`。
- `upx` 同时迁移原脚本生成的旧 `xr.json`，保留端口、UUID、密钥、协议与路由；替换前备份为 `xr.json.bak` 和 `xray.bak`。
- 依赖 `jq`、`unzip`（root 自动尝试安装；非 root 需要预先安装）。GitHub API 不可用或限流时会退出，不回退到作者打包的内核。
- 已用官方 Xray **v26.10.31** 校验 9 种 Xray 入站单独/组合配置及直连/WARP 路由。WebSocket、VMess 的官方弃用警告仍可能出现，保留这些协议以兼容原有节点。
- 未来内核若再次破坏配置兼容性，脚本会在校验阶段停止，仍需针对新的格式更新模板；不能保证自动适配尚未发布的配置规范。

### GeoSite / GeoIP 规则库

安装或执行 `upx` 时，同时下载 [XTLS/Xray-rules-dat](https://github.com/XTLS/Xray-rules-dat) 最新正式发布中的 `geosite-expand.dat` 和 `geoip-full.dat`，保存为 `$HOME/agsbx/geosite.dat`、`geoip.dat`（root 默认路径为 `/root/agsbx/`）。与 Xray 官方安装器使用同一来源，独立于内核发布周期。

已安装用户可直接补装或独立更新规则库：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/weiweibunan/argosbx/main/argosbx.sh) upgeo
```

更新成功后重启 Xray 加载规则库；不重写 `xr.json`，不修改 UUID、端口及已有分流。下载校验、规则库解析和现有配置检查全部通过后才替换，并保留 `.bak` 备份。未新增定时任务。旧快捷命令可能仍指向旧脚本，首次请使用上面的完整命令。

之后可在 `routing.rules` 中引用 `geosite:cn`、`geoip:cn` 等规则（类别需在该规则库中存在）。自定义规则应放在原有兜底规则之前；脚本不会自动决定哪些流量直连或走 WARP。执行 `rep` 仍按上游行为重建配置，因此已有自定义分流时请使用 `upgeo` 或 `upx` 更新。

规则库回归测试：`python3 tests/test_geodata.py /path/to/xray /path/to/geoip.dat /path/to/geosite.dat`。

### 使用本 Fork

将原命令的脚本地址替换为下方地址，前面的协议变量保持原样：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/weiweibunan/argosbx/main/argosbx.sh)
```

已安装旧版时，更新 Xray 并迁移现有 `xr.json`（无需重置协议）：

```bash
bash <(curl -fsSL https://raw.githubusercontent.com/weiweibunan/argosbx/main/argosbx.sh) upx
```

原项目网页生成器和 Docker/容器入口仍是上游实现；需要本修改时请使用上面的主脚本地址。

验证：`bash -n argosbx.sh`，以及 `python3 tests/test_xray.py /path/to/official/xray`（需要 jq、openssl；隔离生成，不安装服务）。配置检查不等于 VPS 网络连通性实测。

---

## Argosbx一键无交互小钢炮脚本💣：极简 + 轻量 + 快速

---------------------------------------

<img width="757" height="255" alt="d89e2542c513e705106371acc7fa1d33" src="https://github.com/user-attachments/assets/7d7a4678-4223-478c-afe2-d303ba0f85a4" />

---------------------------------------

#### 1、基于Sing-box + Xray + Cloudflared-Argo 三内核自动分配

#### 2、支持主流VPS系统（推荐Ubuntu系统），SSH脚本支持非root环境运行，无脑一次回车搞定

#### 3、支持各种容器系统，Docker镜像部署，公开镜像库：```ygkkk/argosbx```

#### 4、根据Sing-box与Xray不同内核，可选15种WARP出站组合，更换落地IP为WARP的IP，解锁流媒体

#### 5、客户端支持方面，各类单协议分享、clash/mihomo/singbox聚合订阅分享都可支持

#### 6、所有代理协议都无需域名（除了argo固定隧道、IP端口CDN），支持单个或多个代理协议任意组合并快速重置更换
【 已支持：Naiveproxy、Vless-xhttp-tls、AnyTLS、Any-reality、Vless-xhttp-reality-vison-enc、Vless-tcp-reality-vision、Vless-xhttp-vison-enc、Vless-ws-vision-enc、Shadowsocks-2022、Vmess-ws、Socks5、Hysteria2、Tuic、Argo临时/固定隧道支持Vless-ws-vision-enc或Vmess-ws 】

#### 7、建议配合SSH一键脚本命令生成器网页使用：https://yonggekkk.github.io/argosbx/

#### 8、如需要多样的功能，推荐使用VPS专用五合一脚本[Sing-box-yg](https://github.com/yonggekkk/sing-box-yg)

#### 9、Argosbx客户端推荐：

安卓手机客户端：[Nekobox-starifly版(全协议支持)](https://github.com/starifly/NekoBoxForAndroid/releases)、[V2rayNG官方版](https://github.com/2dust/v2rayNG/releases)、[Singbox官方版](https://github.com/SagerNet/sing-box/releases)、Clash/Mihomo客户端随意

电脑win客户端：[V2rayN官方版(全协议支持)](https://github.com/2dust/v2rayN/releases)、[Singbox官方版](https://github.com/SagerNet/sing-box/releases)、Clash/Mihomo客户端随意

苹果IOS客户端：小火箭Shadowrocket、Onexray、Sing-bos MT、Clash mi

注：个别协议仅支持某些客户端


------------------------------------------------------------------

* #### 如下图：一键SSH命令生成器：[点击视频教程](https://youtu.be/4u6W4c-t3oU)

<img width="726" height="741" alt="image" src="https://github.com/user-attachments/assets/622fbc56-1058-45c6-8cac-dc00bb6cf6d0" />

------------------------------------------------------------------

* #### 如下图：从此抛弃第三方独立的WARP脚本，xray+singbox双内核集成15种WARP出站组合：[点击视频教程](https://youtu.be/iywjT8fIka4)

<img width="1015" height="681" alt="e0b66a115b1cd6a5060c38cae6e45c55" src="https://github.com/user-attachments/assets/06e69e8e-f714-4ba5-a519-f09fdecb0bbf" />

----------------------------------------------------------

* #### 如下图：节点IP、端口被封依旧可用！套CDN优选5大方案三步视频教程：
  
[视频1：80系+回源cdn](https://youtu.be/RnUT1CNbCr8)

[视频2：Argo临时/固定隧道区别与设置](https://youtu.be/K35NhrNiLK8)

[视频3：黑科技80端口CDN](https://youtu.be/X8BFVyeiY9g)

<img width="1776" height="960" alt="f51af75fcc76bae7e76fe0ef5b9ecc86" src="https://github.com/user-attachments/assets/028b780d-bd48-4c79-8c60-940b3c3d1937" />

---------------------------------------------------------


#### 相关教程可参考[甬哥博客](https://ygkkk.blogspot.com/2025/08/argosb.html)，视频教程如下：

[Argosbx小钢炮脚本重大更新：加入NaiveProxy与XHTTP-TLS一键部署；XHTTP的UDP模式支持CDN优选IP](https://youtu.be/NMJIG_2N2a8)

[Argosbx一键生成SSH命令；解决IP限制、IP质量太差问题；Argo固定隧道设置要点](https://youtu.be/xHzZFP_ywLs)

[搭建代理9大问题排行榜：第4名全网99%的人被误导！第1名每个人都被折腾到爆！](https://youtu.be/pJwJBqBkcfw)

[2025年度代理协议"拉到夯"综合排名](https://youtu.be/IoFtykGXDao)

[ArgoSBX小钢炮脚本更新说明：新增VLESS ENC抗量子加密；80端口也能开启TLS加密？无需域名也能CDN优选？](https://youtu.be/X8BFVyeiY9g)

[Argo隧道代理节点终极教程：VPS+容器搭建最强CDN节点 | 无视端口IP被封 | Argo临时/固定隧道区别 | CDN优选IP加速](https://youtu.be/K35NhrNiLK8)

[ArgoSBX一键无交互小钢炮脚本💣（四）：一键SSH命令生成器发布，只要点几下，各大代理协议任你选](https://youtu.be/4u6W4c-t3oU)

[ArgoSB一键无交互小钢炮脚本💣（三）：内置15种WARP出站组合，轻松替代独立的WARP脚本](https://youtu.be/iywjT8fIka4)

[ArgoSB一键无交互小钢炮脚本💣（二）：代理节点的IP、端口被封依旧可用！ArgoSB脚本套CDN优选4大方案教程](https://youtu.be/RnUT1CNbCr8)

[ArgoSB一键无交互小钢炮脚本💣（一）：VPS/nat VPS在主协议下的应用；仅按一次回车，多协议自由搭配](https://youtu.be/CiXmttY7mhw)

----------------------------------------------------------

### 交流平台：[甬哥博客地址](https://ygkkk.blogspot.com)、[甬哥YouTube频道](https://www.youtube.com/@ygkkk)、[甬哥TG电报群组](https://t.me/+jZHc6-A-1QQ5ZGVl)、[甬哥TG电报频道](https://t.me/+DkC9ZZUgEFQzMTZl)

----------------------------------------------------------
### 感谢支持！微信打赏甬哥侃侃侃ygkkk
![41440820a366deeb8109db5610313a1](https://github.com/user-attachments/assets/e5b1f2c0-bd2c-4b8f-8cda-034d3c8ef73f)

----------------------------------------------------------
### 感谢你右上角的star🌟
[![Stargazers over time](https://starchart.cc/yonggekkk/ArgoSB.svg)](https://starchart.cc/yonggekkk/ArgoSB)

----------------------------------------------------------
### 声明：所有代码来源于Github社区与ChatGPT的整合
