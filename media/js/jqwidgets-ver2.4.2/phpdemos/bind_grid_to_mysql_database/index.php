<!DOCTYPE html>
<html lang="en">
<head>
    <link rel="stylesheet" href="../../jqwidgets/styles/jqx.base.css" type="text/css" />
    <link rel="stylesheet" href="../../jqwidgets/styles/jqx.classic.css" type="text/css" />
    <script type="text/javascript" src="../../scripts/jquery-1.7.2.min.js"></script>
    <script type="text/javascript" src="../../jqwidgets/jqxcore.js"></script>
    <script type="text/javascript" src="../../jqwidgets/jqxbuttons.js"></script>
    <script type="text/javascript" src="../../jqwidgets/jqxscrollbar.js"></script>
    <script type="text/javascript" src="../../jqwidgets/jqxmenu.js"></script>
    <script type="text/javascript" src="../../jqwidgets/jqxdata.js"></script>
    <script type="text/javascript" src="../../jqwidgets/jqxgrid.js"></script>
    <script type="text/javascript" src="../../jqwidgets/jqxgrid.selection.js"></script>	
    <script type="text/javascript">
        $(document).ready(function () {
            // prepare the data
            var source =
            {
                datatype: "json",
                datafields: [
                    { name: 'CompanyName'},
                    { name: 'ContactName'},
                    { name: 'ContactTitle'},
                    { name: 'Address'},
                    { name: 'City'},
                ],
                url: 'data.php'
            };

            var dataAdapter = new $.jqx.dataAdapter(source);
			
			$("#jqxgrid").jqxGrid(
            {
                source: source,
                theme: 'classic',
                columns: [
                  { text: 'Company Name', datafield: 'CompanyName', width: 250},
                  { text: 'ContactName', datafield: 'ContactName', width: 150 },
                  { text: 'Contact Title', datafield: 'ContactTitle', width: 180 },
                  { text: 'Address', datafield: 'Address', width: 200 },
                  { text: 'City', datafield: 'City', width: 120 }
              ]
            });        
        });
    </script>
</head>
<body class='default'>
   <div id="jqxgrid"></div>
</body>
</html>
