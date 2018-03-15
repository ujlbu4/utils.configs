from sure import expect

import configs

from pyhocon import ConfigFactory
from pyhocon.exceptions import ConfigMissingException


class TestConfig:
    def test_merge_defaults_base(self):
        """
        Application config should be merging to reference config (application_conf will rewrite reference_conf values if they exist)
        :return:
        """
        application_conf = ConfigFactory.from_dict({"facade": {"base_url": "http://config1.url"}, "logging": {"config": "config1.yaml"}})
        reference_conf = ConfigFactory.from_dict({"facade": {"base_url": "http://config2.url"}})

        config = configs.merge_configs(reference_conf, application_conf)

        # facade.base_url rewrite by application_conf
        config.get("facade.base_url").should.be.equal("http://config1.url")

        # logging.config merged
        config.get("logging.config").should.be.equal("config1.yaml")

    def test_merge_defaults_application_conf_empty(self):
        application_conf = ConfigFactory.parse_file("unexist_application_conf_file", required=False)
        reference_conf = ConfigFactory.from_dict({"facade": {"base_url": "http://config2.url"}})

        config = configs.merge_configs(reference_conf, application_conf)

        # facade.base_url rewrite by application_conf
        config.get("facade.base_url").should.be.equal("http://config2.url")

        # logging.config absent
        expect(config.get).when.called_with("logging.config").should.have.raised(ConfigMissingException)

    def test_merge_defaults_reference_conf_empty(self):
        application_conf = ConfigFactory.from_dict({"facade": {"base_url": "http://config1.url"}, "logging": {"config": "config1.yaml"}})
        reference_conf = ConfigFactory.parse_file("unexist_referece_conf_file", required=False)

        config = configs.merge_configs(reference_conf, application_conf)

        # facade.base_url rewrite by application_conf
        config.get("facade.base_url").should.be.equal("http://config1.url")

        # logging.config merged
        config.get("logging.config").should.be.equal("config1.yaml")

    def test_merge_root_false(self):
        current_config = ConfigFactory.from_dict({"facade": {"base_url": "http://global.url"}})
        config_from_file = ConfigFactory.from_dict({"facade": {"base_url": "http://from_file.url"}})

        config = configs.merge_root(current_config, config_from_file, is_root=False)

        # facade.base_url rewrite by file config
        config.get("facade.base_url").should.be.equal("http://global.url")

    def test_merge_root_true(self):
        current_config = ConfigFactory.from_dict({"facade": {"base_url": "http://global.url"}})
        config_from_file = ConfigFactory.from_dict({"facade": {"base_url": "http://from_file.url"}})

        config = configs.merge_root(current_config, config_from_file, is_root=True)

        # facade.base_url rewrite by file config
        config.get("facade.base_url").should.be.equal("http://from_file.url")

    def test_load(self):
        config = configs._load(__file__, config_folder_name="data", application_conf="config1.conf", reference_conf="config2.conf")

        config.get("facade.base_url").should.be.equal("http://config1.url")
        config.get("logging.config").should.be.equal("config1.yaml")

    def test_load_tilda(self):
        config = configs._load(__file__, config_folder_name="data", application_conf="config1.conf", reference_conf="config2.conf")

        config.get("facade.base_url~qa").should.be.equal("http://config1-qa.url")
        config.get("logging.config").should.be.equal("config1.yaml")

    def test_load_empty_configs(self):
        config = configs._load(__file__, config_folder_name="data", application_conf="unexist1.conf", reference_conf="unexist2.conf")

        config.as_plain_ordered_dict().should.be.equal({})

    def test_collapse_config_env_vars_exist_env(self):
        config = ConfigFactory.from_dict({"facade": {"base_url": "http://base.url",
                                                     "base_url~qa": "http://base-qa.url"}})

        config = configs.collapse_environment(config, env="qa")

        config.get("facade.base_url").should.be.equal("http://base-qa.url")

    def test_collapse_config_env_vars_unexist_env(self):
        # un-exist env
        config = ConfigFactory.from_dict({"facade": {"base_url": "http://base.url",
                                                     "base_url~qa": "http://base-qa.url"}})

        config = configs.collapse_environment(config, env="prod")

        config.get("facade.base_url").should.be.equal("http://base.url")
        expect(config.get).when.called_with("facade.base_url~qa").should.have.raised(ConfigMissingException)

    def test_collapse_config_env_vars_empty_env(self):
        # empty env
        config = ConfigFactory.from_dict({"facade": {"base_url": "http://base.url",
                                                     "base_url~qa": "http://base-qa.url"}})

        config = configs.collapse_environment(config, env="")

        config.get("facade.base_url").should.be.equal("http://base.url")
        config.get("facade.base_url~qa").should.be.equal("http://base-qa.url")

        config = configs.collapse_environment(config, env=None)

        config.get("facade.base_url").should.be.equal("http://base.url")
        config.get("facade.base_url~qa").should.be.equal("http://base-qa.url")

    def test_collapse_config_env_vars_empty_base(self):
        # empty base
        config = ConfigFactory.from_dict({"facade": {"base_url~qa": "http://base-qa.url"}})

        config = configs.collapse_environment(config, env="qa")

        config.get("facade.base_url").should.be.equal("http://base-qa.url")

    def test_collapse_config_env_vars_nested_vars(self):
        config = ConfigFactory.from_dict(
            {"kafka":
                {"topics":
                    {
                        "user_commands": "base",
                        "user_commands~qa": "qa"
                    }
                }
            }
        )

        config = configs.collapse_environment(config, env="qa")

        config.get("kafka.topics.user_commands").should.be.equal("qa")
