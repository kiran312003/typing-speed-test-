<?php
$a = [9,2,5,7,4];
$o= 'asc';

if($o ===  'asc'){
    sort($a);
}elseif($o === 'desc'){
    rsort($a);
}
echo 'Sorted array:'.imlopde(',',$a);
?>