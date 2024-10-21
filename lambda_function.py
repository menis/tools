import boto3

#Script parameters
ALARM_NAME = 'Idle-EC2-Instance-LessThan10Pct-CPUUtilization-15Min'
TAG_NAME = 'AutoShutdown'
TAG_VALUES = ['true']
region = 'us-west-2'

def lambda_handler(event, context):
    #Create EC2 Client
    ec2Client = boto3.resource('ec2')

    #Grab all instance ids filtered by tag, ignore terminated or terminating 
    all_instance_ids = []
    for instance in ec2Client.instances.filter(Filters=[{'Name': 'tag:'+TAG_NAME, 'Values': TAG_VALUES}, {'Name': 'instance-state-name', 'Values': ['running','pending','stopping','stopped']}]):
        all_instance_ids.append(instance.id)

    #Create CloudWatch Client
    cloudWatchClient = boto3.client('cloudwatch')
 
    #Grab all instances with alarms attached
    response = cloudWatchClient.describe_alarms()

    #Filter for instances with a specific alarm name
    all_instance_ids_with_alarm = []
    for record in response['MetricAlarms']:
        if ALARM_NAME in record['AlarmName']:
            for instance in record['Dimensions']:
                all_instance_ids_with_alarm.append(instance['Value'])

    #Get all instances with tag that don't have an alarm attached
    tagged_instances_without_an_alarm = set(all_instance_ids) - set(all_instance_ids_with_alarm)

    #Iterate over instances and setup an alarm
    for instance in tagged_instances_without_an_alarm:
        #Configuration parameters for the alarm
        AlarmName = ALARM_NAME+'_'+instance
        AlarmDescription = 'Triggered when CPUUtilization < 10 for 1 consecutive 15 min periods.'
        ActionsEnabled=True
        AlarmActions = ['arn:aws:automate:'+region+':ec2:stop']
        MetricName='CPUUtilization'
        Namespace='AWS/EC2'
        Statistic='Average'
        Dimensions=[{"Name":"InstanceId","Value": instance}]
        Period=900
        EvaluationPeriods=1
        DatapointsToAlarm=1
        Threshold=10
        ComparisonOperator= 'LessThanThreshold'

        cloudWatchClient.put_metric_alarm(AlarmName=AlarmName, AlarmDescription=AlarmDescription, ActionsEnabled=ActionsEnabled, AlarmActions=AlarmActions, MetricName=MetricName, Namespace=Namespace, Statistic=Statistic, Dimensions=Dimensions, Period=Period, EvaluationPeriods=EvaluationPeriods, DatapointsToAlarm=DatapointsToAlarm, Threshold=Threshold, ComparisonOperator=ComparisonOperator)
        print('Added alarm to instance ' + instance)
