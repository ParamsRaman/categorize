<?php
#Include the connect.php file
include('connect.php');
#Connect to the database
//connection String
$connect = mysql_connect($hostname, $username, $password)
or die('Could not connect: ' . mysql_error());
//Select The database
$bool = mysql_select_db($database, $connect);
if ($bool === False){
   print "can't find $database";
}
// get data and store in a json array
$query = "SELECT * FROM Employees";

if (isset($_GET['insert']))
{
	// INSERT COMMAND 
	$insert_query = "INSERT INTO `Employees`(`FirstName`, `LastName`, `Title`, `Address`, `City`, `Country`, `Notes`) VALUES ('".$_GET['FirstName']."','".$_GET['LastName']."','".$_GET['Title']."','".$_GET['Address']."','".$_GET['City']."','".$_GET['Country']."','".$_GET['Notes']."')";
	
   $result = mysql_query($insert_query) or die("SQL Error 1: " . mysql_error());
   echo $result;
}
else if (isset($_GET['update']))
{
	// UPDATE COMMAND 
	$update_query = "UPDATE `Employees` SET `FirstName`='".$_GET['FirstName']."',
	`LastName`='".$_GET['LastName']."',
	`Title`='".$_GET['Title']."',
	`Address`='".$_GET['Address']."',
	`City`='".$_GET['City']."',
	`Country`='".$_GET['Country']."',
	`Notes`='".$_GET['Notes']."' WHERE `EmployeeID`='".$_GET['EmployeeID']."'";
	 $result = mysql_query($update_query) or die("SQL Error 1: " . mysql_error());
     echo $result;
}
else if (isset($_GET['delete']))
{
	// DELETE COMMAND 
	$delete_query = "DELETE FROM `Employees` WHERE `EmployeeID`='".$_GET['EmployeeID']."'";	
	$result = mysql_query($delete_query) or die("SQL Error 1: " . mysql_error());
    echo $result;
}
else
{
    // SELECT COMMAND
	$result = mysql_query($query) or die("SQL Error 1: " . mysql_error());
	while ($row = mysql_fetch_array($result, MYSQL_ASSOC)) {
		$employees[] = array(
			'EmployeeID' => $row['EmployeeID'],
			'FirstName' => $row['FirstName'],
			'LastName' => $row['LastName'],
			'Title' => $row['Title'],
			'Address' => $row['Address'],
			'City' => $row['City'],
			'Country' => $row['Country'],
			'Notes' => $row['Notes']
		  );
	}
	 
	echo json_encode($employees);
}
?>