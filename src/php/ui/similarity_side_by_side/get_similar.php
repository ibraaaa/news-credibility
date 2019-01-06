<html>
<head>
<title>News Similarity</title>
</head>
<body>

<FORM NAME ="form1" METHOD ="POST" ACTION = "get_similar.php">

<INPUT TYPE = "TEXT" VALUE ="" NAME="query_url">
<INPUT TYPE = "Submit" Name = "submit_btn" VALUE = "Submit">

</FORM>

<?php
if (isset($_POST['submit_btn'])) {
	$item = $_POST['query_url'];
	$ret = exec("PYTHONPATH=/home/ibraaaa/contents/Master/code/news-credibility/src/python/:/home/ibraaaa/contents/Master/code/news-credibility/lib/ /usr/bin/python ../../../python/run_sim.py '$item'", $output);
	var_dump($output);
	echo "<html dir='rtl'>";
	echo '<table border="2">';
	foreach ($output as $value) {
		echo "<tr>";
		echo "<td>";
		list($url, $path, $news_site, $date, $score, $sentiment_score) = split(",",  $value);
		$url = substr($url, 1);
		$url = trim(substr($url, 0, strlen($url) - 1));
		echo '<table border="1">';
		echo "<tr>";
		echo "<td>";
		echo "</br> <a href=\"" . $url . "\">". $news_site . "</a></br>";
		echo "</td>";
		echo "<td>";
		echo $date;
		echo "</td>";
		echo "</tr>";
		echo "</table>";
		$path = substr($path, 1);
		$path = trim(substr($path, 0, strlen($path) - 1));
		$file_path = "../../../" . $path;
		$file_handle = fopen($file_path, "r");
	
		$i = 0;
		while (!feof($file_handle)) {
			$line = fgets($file_handle);
			echo $line . "</br>";
			$i += 1;
			if ($i > 1)
				break;
		}
		fclose($file_handle);
		echo "</td>";
		echo "<td>";
		echo '<table border="1">';
		echo "<td>";
		echo $score;
		echo "</td>";
		echo "<td>";
		echo $sentiment_score;
		echo "</td>";
		echo "</table>";
		echo "</td>";
		echo "</tr>";
	}
	echo "</table>";
}
?>

</body>
</html>
