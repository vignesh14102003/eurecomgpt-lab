
# Phase 1 — Comparison Report

## 1. Setup facts

**Your image size**, in MB:

<!--answer:image_size_mb-->
50.25
<!--/answer-->

**The custom VPC and subnet you created:**

<!--answer:vpc_name-->
echo-net
<!--/answer-->

<!--answer:subnet_name-->
echo-subnet
<!--/answer-->

---

## 2. Measurements

| Platform | Cold (ms) | Warm median (ms) |
|---|---:|---:|
| IaaS VM | <!--answer:vm_cold_ms-->283.0<!--/answer--> | <!--answer:vm_warm_median_ms-->213.0<!--/answer--> |
| Cloud Run | <!--answer:cloudrun_cold_ms-->3554.1<!--/answer--> | <!--answer:cloudrun_warm_median_ms-->639.1<!--/answer--> |
| Cloud Function | <!--answer:function_cold_ms-->2469.4<!--/answer--> | <!--answer:function_warm_median_ms-->637.8<!--/answer--> |

### Warm latency comparison

<!--answer:latency_plot-->
```text
Warm median latency (each # is approximately 16 ms)

VM             213.0 ms  #############
Cloud Run      639.1 ms  ########################################
Cloud Function 637.8 ms  ########################################
```
<!--/answer-->

---

## 3. Per-platform analysis

**Scaling behaviour**

<!--answer:scaling_behaviour-->
The VM does not automatically create additional VMs when requests increase. All requests reach the single e2-micro instance, whose capacity is limited by its allocated CPU and memory. Cloud Run can automatically create more container instances as demand increases, but I configured a maximum of three instances and allowed scaling to zero when idle. The Gen 2 Cloud Function also scales its managed instances on demand and can scale to zero. I did not explicitly set a maximum instance count for the function, so its upper limit depends on the applicable platform and function configuration.
<!--/answer-->

**Deployment effort**

<!--answer:deployment_effort-->
The VM required the most manual work. I created a custom VPC and subnet, configured firewall rules, created the e2-micro instance, granted Artifact Registry access, installed Docker, authenticated to the registry and started the container. I also had to test connectivity and maintain the VM. Cloud Run required building and uploading the Docker image, followed by configuring a public service, port 8080 and instance scaling limits. For the Gen 2 Cloud Function, I deployed the Python source with an HTTP trigger and the echo entry point. Google Cloud managed the function build and runtime. The application logic was shared, but the deployment and infrastructure responsibilities differed.
<!--/answer-->

---

## 4. Why do two of your three numbers look alike?

**Complete output of `gcloud run services list`:**

<!--answer:run_services_list-->
```text
✓
SERVICE: echo
REGION: us-central1
URL: https://echo-79704069078.us-central1.run.app
LAST DEPLOYED BY: service-79704069078@gcf-admin-robot.iam.gserviceaccount.com
LAST DEPLOYED AT: 2026-10-27T04:56:39.791405Z

✓
SERVICE: echo-bot
REGION: us-central1
URL: https://echo-bot-79704069078.us-central1.run.app
LAST DEPLOYED BY: Vignesh.Ramkumar@eurecom.fr
LAST DEPLOYED AT: 2026-10-27T04:51:21.530790Z
```
<!--/answer-->

**Convergence explanation**

<!--answer:convergence_explanation-->
The service list shows two Cloud Run services in us-central1. The service named `echo` was deployed by the Cloud Functions administration service account, while `echo-bot` was deployed directly by my user account. This indicates that the Gen 2 Cloud Function is backed by a managed Cloud Run service. Both deployments therefore use related managed container infrastructure and can scale down when idle, which helps explain their similar warm median latencies: 639.1 ms for Cloud Run and 637.8 ms for the function. Their cold measurements differed in this run: 3554.1 ms for Cloud Run and 2469.4 ms for the function. Both were slower than the already-running VM. The deployment paths still differ: Cloud Run received my prebuilt Docker image, while the Functions API accepted Python source code and deployed it using the `echo` entry point.
<!--/answer-->
