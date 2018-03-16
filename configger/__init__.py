from pyhocon import ConfigFactory as TypesafeConfigFactory, ConfigTree

import os

# will import only once, so it will store all updates (unless it will be override)
config = ConfigTree(root=True)


def _load(src_invoking_file, config_folder_name="configs", application_conf="application.conf", reference_conf="reference.conf"):
    package_path = os.path.dirname(src_invoking_file)

    local_application_conf = ConfigTree(TypesafeConfigFactory
                                        .parse_file('{package_path}/{config_folder_name}/{application_conf}'
                                                    .format(package_path=package_path,
                                                            config_folder_name=config_folder_name,
                                                            application_conf=application_conf),
                                                    required=False))
    local_reference_conf = ConfigTree(TypesafeConfigFactory
                                      .parse_file('{package_path}/{config_folder_name}/{reference_conf}'
                                                  .format(package_path=package_path,
                                                          config_folder_name=config_folder_name,
                                                          reference_conf=reference_conf),
                                                  required=False))

    # c = merge_configs(local_reference_conf, local_application_conf)
    c = local_application_conf.with_fallback(local_reference_conf)

    return c


def merge_configs(left, right):
    """
    Merge config right into left
    """
    c = right
    if len(left) > 0:
        if len(right) > 0:
            c = ConfigTree.merge_configs(left, right)
        else:
            c = left

    return c


def merge_root(config_current, config_from_file, is_root):
    if is_root:
        updated_conf = merge_configs(config_current, config_from_file)
    else:
        updated_conf = merge_configs(config_from_file, config_current)

    return updated_conf


def load_config(file, is_root=False):
    # if not isinstance(current_config, ConfigTree):
    #     raise TypeError('A current_config must be a [{}] type'.format(ConfigTree))
    global config

    c = _load(file)

    updated_conf = merge_root(config, c, is_root)

    set_global(updated_conf)
    return updated_conf


def set_global(new_conf):
    global config
    config = new_conf


def collapse_environment(config, env):
    env_config = ConfigTree()

    if not env:
        return config

    # filter env attr
    for item in config:
        if not isinstance(config[item], dict):
            continue

        for k, v in config[item].items():
            if isinstance(config[item], dict):
                # update nested elements
                config[item] = collapse_environment(config[item], env)

            if k.find("~{env}".format(env=env)) > 0:
                k = k.replace("~{env}".format(env=env), "")
                env_config.put(item, TypesafeConfigFactory.from_dict({k: v}), append=True)

    # merge env values to source config
    config = merge_configs(config, env_config)

    # remove others env attrs
    result = ConfigTree()
    for item in config:
        if not isinstance(config[item], dict):
            if item.find("~") < 0:  # not found
                result.put(item, config[item])
            continue

        for k, v in config[item].items():
            if k.find("~") < 0:  # not found
                result.put(item, TypesafeConfigFactory.from_dict({k: v}), append=True)

    return result
