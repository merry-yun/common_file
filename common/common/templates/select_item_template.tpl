/*
 * {{table.scheme}}.{{table.name}}
 * Comment: {{table.comment}}
 * created by {{ USER }}
 * created at {{ NOWTIME }}
 * 这是一个自动生成sql-select类型的文件
 * 每日动动脑，人人没烦恼
 * ~~~~~ {{ USER }}快点夸我夸我
 */

 SELECT
 {% for field in fields %}{% if field.comment  %}{{table.TABLENAME}}.{{field.name}} AS "{{field.comment}}", {% else %}{{table.TABLENAME}}.{{field.name}},{% endif %}
 {% endfor %}"{{table.name}}" AS "来源数据爬虫表名",
 "{{table.scheme}}" AS "来源数据爬虫库名"
 FROM {{table.scheme}}.{{table.name}} as {{table.TABLENAME}};

