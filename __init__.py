# -*- coding: utf-8 -*-
# 하위 폴더의 패키지를 import 하도록 수정
from .khd4_plugin.khd4_plugin import Khd4MetadataProvider

metadata_providers = [
    Khd4MetadataProvider,
]
