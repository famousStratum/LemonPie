"""Argument-parsing tests for `lm` (lemonpie.cli.parser) and `lmConfig`
(lemonpie.cli.config_cmd). These only exercise parser.parse_args() — no config
files, no sessions, no network — so they don't need the isolated_dirs fixture.
"""

import pytest

from lemonpie.cli.config_cmd import build_parser as build_lmconfig_parser
from lemonpie.cli.parser import build_parser as build_lm_parser


class TestLmParser:
    def test_default_no_args(self):
        args = build_lm_parser().parse_args([])
        assert args.model is None
        assert args.new is False
        assert args.session is None
        assert args.list is False
        assert args.delete is None
        assert args.title is None
        assert args.close is False
        assert args.print is False
        assert args.delete_all is False
        assert args.prompt == []

    def test_prompt_is_collected_as_list(self):
        args = build_lm_parser().parse_args(["tell", "me", "a", "joke"])
        assert args.prompt == ["tell", "me", "a", "joke"]

    def test_model_flag_short_and_long_forms_agree(self):
        assert build_lm_parser().parse_args(["-m", "qwen"]).model == "qwen"
        assert build_lm_parser().parse_args(["--model", "qwen"]).model == "qwen"

    def test_new_session_flag_with_prompt(self):
        args = build_lm_parser().parse_args(["-n", "hello"])
        assert args.new is True
        assert args.prompt == ["hello"]

    def test_list_flag(self):
        assert build_lm_parser().parse_args(["-l"]).list is True

    def test_delete_takes_a_session_id(self):
        args = build_lm_parser().parse_args(["-d", "20260101-000000"])
        assert args.delete == "20260101-000000"

    def test_delete_all_is_distinct_from_delete(self):
        args = build_lm_parser().parse_args(["--delete-all"])
        assert args.delete_all is True
        assert args.delete is None

    def test_title_combined_with_prompt(self):
        args = build_lm_parser().parse_args(["-t", "My title", "hi", "there"])
        assert args.title == "My title"
        assert args.prompt == ["hi", "there"]

    def test_session_flag_takes_an_id(self):
        args = build_lm_parser().parse_args(["-s", "20260101-000000"])
        assert args.session == "20260101-000000"

    def test_close_flag(self):
        assert build_lm_parser().parse_args(["-c"]).close is True

    def test_print_flag(self):
        assert build_lm_parser().parse_args(["-p"]).print is True

    def test_version_flag_exits_zero_and_prints(self, capsys):
        with pytest.raises(SystemExit) as exc_info:
            build_lm_parser().parse_args(["-v"])
        assert exc_info.value.code == 0
        assert capsys.readouterr().out.startswith("lm ")


class TestLmConfigParser:
    def test_no_args_all_defaults(self):
        args = build_lmconfig_parser().parse_args([])
        assert args.host is None
        assert args.default_model is None
        assert args.add_model is None
        assert args.remove_model is None
        assert args.list_models is False
        assert args.show is False
        assert args.force is False

    def test_host(self):
        args = build_lmconfig_parser().parse_args(["--host", "http://127.0.0.1:11434"])
        assert args.host == "http://127.0.0.1:11434"

    def test_add_model_takes_alias_and_name(self):
        args = build_lmconfig_parser().parse_args(["--add-model", "qwen", "qwen2.5-coder:3b"])
        assert args.add_model == ["qwen", "qwen2.5-coder:3b"]

    def test_add_model_with_force(self):
        args = build_lmconfig_parser().parse_args(
            ["--add-model", "qwen", "qwen2.5-coder:3b", "--force"]
        )
        assert args.force is True

    def test_remove_model_takes_an_identifier(self):
        args = build_lmconfig_parser().parse_args(["--remove-model", "qwen"])
        assert args.remove_model == "qwen"

    def test_list_models_flag(self):
        assert build_lmconfig_parser().parse_args(["--list-models"]).list_models is True

    def test_default_model_takes_an_identifier(self):
        args = build_lmconfig_parser().parse_args(["--default-model", "qwen"])
        assert args.default_model == "qwen"

    def test_show_flag(self):
        assert build_lmconfig_parser().parse_args(["--show"]).show is True
