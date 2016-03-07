#!/usr/bin/env php
<?php

# include phabricator libraries
$root = dirname(dirname(__FILE__));
require_once $root.'/scripts/__init_script__.php';

# User
function getAdmin()
{
    $username = 'admin';
    $user = id(new PhabricatorUser())->loadOneWhere(
        'username = %s',
        $username);
    return $user;
}

# Project
function queryProject($project_name)
{
    $user = getAdmin();
    $query = id(new PhabricatorProjectQuery())
        ->withNames(array($project_name))
        ->setViewer($user)
        ->execute();

    $project = reset($query);

    return $project;
}

function addProject($project_name)
{

    $user = getAdmin();
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

function checkProject($project_name)
{
    $user = getAdmin();
    $query = queryProject($project_name);
    if ($query == NULL)
    {
        addProject($project_name);
        $query = queryProject($project_name);
    }
    # return phid
    $project = $query;
    return $project;
}

# tasks
function queryTask($kan_task, $project_id)
{
    $user = getAdmin();
    $query = id(new ManiphestTaskQuery())
        ->setViewer($user)
        ->needProjectPHIDs(true)
        ->withEdgeLogicPHIDs(
            PhabricatorProjectObjectHasProjectEdgeType::EDGECONST,
            PhabricatorQueryConstraint::OPERATOR_AND,
            array($project_id))
            ->execute();

    # match title
    foreach ($query as $task)
    {

        if (strcmp($task->getTitle(), $kan_task["title"] == 0))
            return $task;
    }
    return NULL;
}

function addTask($kan_task,  $project_id)
{
    $user = getAdmin();
    $task = ManiphestTask::initializeNewTask($user);


    $changes = array();
    $transactions = array();

    $changes[ManiphestTransaction::TYPE_TITLE] = $kan_task['title'];
    $changes[ManiphestTransaction::TYPE_DESCRIPTION] = $kan_task['description'];
    $changes[ManiphestTransaction::TYPE_STATUS] = ManiphestTaskStatus::getDefaultStatus();
    $changes[PhabricatorTransactions::TYPE_COMMENT] = null;
    $project_type = PhabricatorProjectObjectHasProjectEdgeType::EDGECONST;
    $transactions[] = id(new ManiphestTransaction())
    ->setTransactionType(PhabricatorTransactions::TYPE_EDGE)
    ->setMetadataValue('edge:type', $project_type)
    ->setNewValue(
      array(
        '=' => array_fuse(array($project_id)),
      ));


    $template = new ManiphestTransaction();

    foreach ($changes as $type => $value) {
      $transaction = clone $template;
      $transaction->setTransactionType($type);
        $transaction->setNewValue($value);
      
      $transactions[] = $transaction;
    }

    $editor = id(new ManiphestTransactionEditor())
        ->setActor($user)
        ->setContentSourceFromConduitRequest(new ConduitAPIRequest(array()))
        ->setContinueOnNoEffect(true);

    $editor->applyTransactions($task, $transactions);
}

function checkTask($kan_task, $project_id)
{
    $query = queryTask($kan_task, $project_id);
    if ($query == NULL)
    {
        addTask($kan_task, $project_id);
        $query = queryTask($kan_task, $project_id);
    }

    $task = $query;
    return $task;
}

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
$kan_projects = $pdo->query($query);
while ($kan_project = $kan_projects->fetch())
{
    $project_name = $kan_project['name'];
    print("checking project " . $project_name . "\n");
    $project = checkproject($project_name);
    $project_id = $project->getPHID();
    # add tasks
    $query = 'SELECT * FROM tasks
                WHERE project_id = ' . $kan_project['id'];
    $kan_tasks = $pdo->query($query);
    while ($kan_task = $kan_tasks->fetch())
    {
        print("\tchecking task " . $kan_task['title'] . "\n");
        $task = checkTask($kan_task, $project_id);
    }

    # $columns = id(new PhabricatorProjectColumnQuery())
    #     ->setViewer($user)
    #     ->withProjectPHIDs(array($project->getPHID()))
    #     ->execute();
    # var_dump($columns);
}

?>
