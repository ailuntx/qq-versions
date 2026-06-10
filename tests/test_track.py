import unittest

from scripts.track import determine_config_url, parse_config


class QQTrackTests(unittest.TestCase):
    def test_determine_config_url(self):
        page = 'var rainbowConfigUrl = "//cdn-go.cn/qq-web/im.qq.com_new/latest/rainbow/linuxConfig.js";'
        self.assertEqual(
            determine_config_url(page),
            "https://cdn-go.cn/qq-web/im.qq.com_new/latest/rainbow/linuxConfig.js",
        )

    def test_parse_config(self):
        config = """
        ;(function(){var params= {"version":"3.2.29","x64DownloadUrl":{"deb":"https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/hash/QQ_3.2.29_260528_amd64_01.deb","appimage":"https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/hash/QQ_3.2.29_260528_x86_64_01.AppImage","rpm":"https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/hash/QQ_3.2.29_260528_x86_64_01.rpm"},"armDownloadUrl":{"deb":"https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/hash/QQ_3.2.29_260528_arm64_01.deb","rpm":"https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/hash/QQ_3.2.29_260528_aarch64_01.rpm","appimage":"https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/hash/QQ_3.2.29_260528_arm64_01.AppImage"},"updateDate":"2026-05-28","loongarchDownloadUrl":"https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/hash/QQ_3.2.29_260528_loongarch64_01.deb","mipsDownloadUrl":"https://qqdl.gtimg.cn/qqfile/QQNT/9.9.31/release/hash/QQ_3.2.29_260528_mips64el_01.deb"};
        })()
        """
        release = parse_config(config)
        self.assertEqual(release["version"], "3.2.29")
        self.assertEqual(release["released"], "2026-05-28T00:00:00+00:00")
        self.assertIn("x86_64", release["packages"])
        self.assertIn("arm64", release["packages"])
        self.assertIn("loongarch64", release["packages"])
        self.assertIn("mips64el", release["packages"])


if __name__ == "__main__":
    unittest.main()
