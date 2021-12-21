# -*- coding: utf-8 -*-
import scrapy

"""

TableDir:
{{table.scheme}}.{{table.name}}
Comment: {{table.comment}}
-- created by {{ USER }}
-- created at {{ NOWTIME }}

 * 这是一个自动生成item文件
 * 每日动动脑，人人没烦恼
 * ~~~~~ {{ USER }} 快点夸我夸我
"""


class {{table.TABLENAME}}Item(scrapy.Item):

    __tablename__ = "{{table.name}}"
    __scheme__ = "{{table.scheme}}"

    {% for field in fields %}{{field.name}} = scrapy.Field()  # `comment:{{field.comment}};type:{{field.type}};key:{{field.key}}`
    {% endfor %}