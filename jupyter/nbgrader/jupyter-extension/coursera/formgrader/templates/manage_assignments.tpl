{%- extends 'base.tpl' -%}

{%- block head -%}
<script>
var url_prefix = "{{ url_prefix }}";
</script>

<script src="{{ base_url }}/formgrader/static/js/manage_assignments.js"></script>
{%- endblock -%}

{%- block title -%}
Manage Assignments
{%- endblock -%}

{%- block sidebar -%}
<li role="presentation" class="active"><a href="{{ base_url }}/formgrader/manage_assignments">Manage Assignments</a></li>
{%- endblock -%}

{%- block breadcrumbs -%}
<ol class="breadcrumb">
  <li class="active">Assignments</li>
</ol>
{%- endblock -%}

{%- block messages -%}
<div class="panel-group" id="accordion" role="tablist" aria-multiselectable="true">
  <div class="panel panel-default">
    <div class="panel-heading" role="tab" id="headingOne">
      <h4 class="panel-title">
        <a class="collapsed" role="button" data-toggle="collapse" data-parent="#accordion" href="#collapseOne" aria-expanded="false" aria-controls="collapseOne">
          Instructions (click to expand)
        </a>
      </h4>
    </div>
    <div id="collapseOne" class="panel-collapse collapse" role="tabpanel" aria-labelledby="headingOne">
      <div class="panel-body">
        <ol>
          <li>To <b>create</b> an assignment, click the "Add new assignment..." button below.</li>
          <li>To <b>edit assignment files</b>, click on the name of an assignment.</li>
          <li>To <b>generate</b> the student version of an assignment, click on the generate button.</li>
          <li>To <b>preview</b> the student version of an assignment, click on the preview button.</li>
          <li>After generating and testing the student version of an assignment, go back to Lab Manager to publish the lab.</li>
        </ol>
      </div>
    </div>
  </div>
</div>

{%- endblock -%}

{%- block table_header -%}
<tr>
  <th>Name</th>
  <th hidden class="text-center">Due Date</th>
  <th hidden class="text-center">Status</th>
  <th hidden class="text-center no-sort">Edit</th>
  <th class="text-center no-sort">Generate</th>
  <th class="text-center no-sort">Preview</th>
  <th hidden class="text-center no-sort">Release</th>
  <th hidden class="text-center no-sort">Collect</th>
  <th hidden class="text-center"># Submissions</th>
  <th hidden class="text-center no-sort">Generate Feedback</th>
  <th hidden class="text-center no-sort">Release Feedback</th>
</tr>
{%- endblock -%}

{%- block table_body -%}
<tr><td colspan="3">Loading, please wait...</td></tr>
{%- endblock -%}

{%- block table_footer -%}
<tr>
  <td colspan="3">
    <span class="glyphicon glyphicon-plus" aria-hidden="true"></span>
    <a href="#" onClick="createAssignmentModal();">Add new assignment...</a>
  </td>
</tr>
{%- endblock -%}
