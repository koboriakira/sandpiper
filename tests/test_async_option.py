"""--async オプションのテスト"""

import sys
from unittest.mock import MagicMock, patch


class TestAsyncOption:
    def test_async_flag_spawns_background_process(self):
        """--async フラグが指定された場合、バックグラウンドプロセスを起動して即座に返ること"""
        original_argv = sys.argv.copy()
        try:
            sys.argv = ["/usr/local/bin/sandpiper", "create-todo", "テスト", "--async"]

            with (
                patch("subprocess.Popen") as mock_popen,
                patch("pathlib.Path.open", MagicMock()),
                patch("sandpiper.main.console") as mock_console,
            ):
                mock_popen.return_value = MagicMock()

                try:
                    from sandpiper.main import main

                    main()
                except SystemExit as e:
                    assert e.code == 0

                # --async を除いた引数でサブプロセスが起動されること
                expected_args = ["/usr/local/bin/sandpiper", "create-todo", "テスト"]
                mock_popen.assert_called_once()
                actual_call_args = mock_popen.call_args[0][0]
                assert actual_call_args == expected_args

                # バックグラウンド実行を示すメッセージが表示されること
                mock_console.print.assert_called_once()
                printed_text = mock_console.print.call_args[0][0]
                assert "受け付けました" in printed_text
        finally:
            sys.argv = original_argv

    def test_async_flag_uses_start_new_session(self):
        """--async フラグ使用時、start_new_session=True でプロセスが起動されること"""
        original_argv = sys.argv.copy()
        try:
            sys.argv = ["/usr/local/bin/sandpiper", "version", "--async"]

            with (
                patch("subprocess.Popen") as mock_popen,
                patch("pathlib.Path.open", MagicMock()),
                patch("sandpiper.main.console"),
            ):
                mock_popen.return_value = MagicMock()

                try:
                    from sandpiper.main import main

                    main()
                except SystemExit:
                    pass

                kwargs = mock_popen.call_args[1]
                assert kwargs.get("start_new_session") is True
                assert kwargs.get("close_fds") is True
        finally:
            sys.argv = original_argv

    def test_no_async_flag_calls_app_normally(self):
        """--async フラグがない場合、通常通り app() が呼ばれること"""
        original_argv = sys.argv.copy()
        try:
            sys.argv = ["/usr/local/bin/sandpiper", "version"]

            with (
                patch("subprocess.Popen") as mock_popen,
                patch("sandpiper.main.app") as mock_app,
            ):
                from sandpiper.main import main

                main()

                mock_app.assert_called_once()
                mock_popen.assert_not_called()
        finally:
            sys.argv = original_argv
