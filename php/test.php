#!/usr/bin/env php
<?php

# include phabricator libraries
$root = dirname(dirname(__FILE__));
require_once $root.'/scripts/__init_script__.php';

# read sqlite DB
try {
    $con = 'sqlite:db.sqlite';
    $pdo = new PDO($con, 'admin', 'admin');
    $pdo->setAttribute(PDO::ATTR_ERRMODE, PDO::ERRMODE_EXCEPTION);
}
catch(PDOException $e) {
    $msg = 'ERREUR PDO dans ' . $e->getFile() . ' L.' . $e->getLine() . ' : ' . $e->getMessage();
    die($msg);
}

$query = 'SELECT * FROM projects';
$res = $pdo->query($query);
while ($cur = $res->fetch())
{
    $project_name = $cur['name'];

    # retrieve admin user
    $username = 'admin';
    $user = id(new PhabricatorUser())->loadOneWhere(
        'username = %s',
        $username);

    $project = PhabricatorProject::initializeNewProject($user);

    $xactions = array();
    # set name
    $xactions[] = id(new PhabricatorProjectTransaction())
        ->setTransactionType(PhabricatorProjectTransaction::TYPE_NAME)
        ->setNewValue($project_name);

    # set members
    $members = array();
    $xactions[] = id(new PhabricatorProjectTransaction())
           ->setTransactionType(PhabricatorTransactions::TYPE_EDGE)
           ->setMetadataValue(
             'edge:type',
             PhabricatorProjectProjectHasMemberEdgeType::EDGECONST)
           ->setNewValue(
             array(
               '+' => array_fuse($members),
             ));

    $editor = id(new PhabricatorProjectTransactionEditor())
           ->setActor($user)
           ->setContinueOnNoEffect(true)
           ->setContentSourceFromConduitRequest(new ConduitAPIRequest(array()));
     
    $editor->applyTransactions($project, $xactions);
}

?>
