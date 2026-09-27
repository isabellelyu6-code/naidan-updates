# 首次启用奶蛋自动更新

仓库：`isabellelyu6-code/naidan-updates`

1. 解压本发布包。
2. 在仓库网页点击 **Add file → Upload files**。
3. 将解压后的全部内容拖入上传区域，保留 `.github/workflows/release.yml`、`assets` 等目录结构。
4. 提交说明可填写 `Publish 奶蛋 v2.1.0`，然后点击 **Commit changes**。
5. 打开仓库的 **Actions** 页面；首次运行若要求确认，点击启用 Actions。
6. 构建完成后，仓库右侧 **Releases** 会出现 `奶蛋 v2.1.0`，其中包含 `奶蛋.exe`。

这一版安装后，奶蛋会从该仓库自动检查后续 Release。以后只需发布更高版本号，无需用户重新下载压缩包。
