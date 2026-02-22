<current_btca_resources>

  <!-- Add one <configured_resource> per project-level BTCA resource. -->

  <!-- Template: git resource -->

<configured_resource>
<name>{resource-name}</name>
<type>git</type>
<url>{https://github.com/org/repo}</url>
<branch>{main}</branch>
<search_paths>{path_one, path_two}</search_paths>
<notes>{short implementation-focused notes}</notes>
</configured_resource>

  <!-- Template: npm resource -->

<configured_resource>
<name>{resource-name}</name>
<type>npm</type>
<package>{npm-package-name}</package>
<notes>{short implementation-focused notes}</notes>
</configured_resource>

  <!-- Template: local resource -->

<configured_resource>
<name>{resource-name}</name>
<type>local</type>
<path>{relative/or/absolute/path}</path>
<search_paths>{path_one, path_two}</search_paths>
<notes>{short implementation-focused notes}</notes>
</configured_resource>
</current_btca_resources>
