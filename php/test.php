#!/usr/bin/env php
<?php

# include phabricator libraries
$root = dirname(dirname(__FILE__));
require_once $root.'/scripts/__init_script__.php';

function checkProjectExist($project_name, $user)
{
    $query = id(new PhabricatorProjectQuery())
        ->withNames(array($project_name))
        ->setViewer($user)
        ->execute();

    if (count($query) == 0)
        return false;
    else
        return true;
}

function createProject($project_name, $user)
{

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

# retrieve admin user
$username = 'admin';
$user = id(new PhabricatorUser())->loadOneWhere(
    'username = %s',
    $username);


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
    if (!checkProjectExist($project_name, $user));
        createProject($project_name, $user);
}

?>
