from cli.src.providers.any.APIProxy import APIProxy
from cli.src.providers.any.InfrastructureBuilder import InfrastructureBuilder
from cli.src.providers.any.InfrastructureConfigCollector import \
    InfrastructureConfigCollector
from cli.src.providers.provider_class_loader import provider_class_loader


def test_provider_class_loader_infrastructurebuilder_any():
    infrastructure_builder = provider_class_loader('any', 'InfrastructureBuilder')
    assert infrastructure_builder is InfrastructureBuilder


def test_provider_class_loader_apiproxy_any():
    api_proxy = provider_class_loader('any', 'APIProxy')
    assert api_proxy is APIProxy


def test_provider_class_loader_infrastructureconfigcollector_any():
    infrastructure_config_collector = provider_class_loader('any', 'InfrastructureConfigCollector')
    assert infrastructure_config_collector is InfrastructureConfigCollector



