# Monitoring of Grafana Dashboards to AX206

This tool intends to be a mechanism for publishing grafana metrics to an AX206 display which has a resolution of 
480x320.   

Purchase here: https://www.amazon.com/Screen-Monitor-Computer-Temperature-Display/dp/B09TTHZYSH

## Installation Requirements

### requirements.txt

Ensure you've setup a local venv environment after pulling down the source code:

```bash
python3 -m venv .
source bin/activate
pip3 install -r requirements.txt
```

This will create a location where you can locally pip3 install all of the dependencies required to run this project,
source the bin/activate script so you can install all of the modules locally.

### Grafana

Before you begin, you need grafana installed on your system which can be installed via your systems package manager.
You will need an authenticated account that can view the dashboards you create in grafana.

Please note that any grafana dashboards you create will be published to a 480x320 resolution LCD screen - this isn't
a-lot of real-estate, sufficient for perhaps 2 rows of graphs and at most 4-5 columns of metrics (single digit metrics).

If you have an NVIDIA graphics card, I would recommend installing dcgm-exporter which publishes prometheus metrics
regarding voltages, temperature and other statistics to a prometheus end-point on your system which can be then graphed.

This installation guide won't go into detail on the setup of grafana / prometheus or system metrics you might want to
measure, but there's plenty of guides available for doing so, please review the appendix in this document for details
on how to get grafana running on your system.

### Configuration

Local to the script grafana-pull.py, the following configuration file must exist.  An example is below

```yaml
grafana:
  url: http://localhost:3000
  username: admin
  password: admin

  dashboards:
    - path: /d/Oxed_c6Wz/nvidia-dcgm-exporter-dashboard?orgId=1&from=now-30m&to=now
      crop_top: 135
    - path: /d/c2fb5419-2842-441d-a109-2677acdb8ba7/system-sensor-data?orgId=1&from=now-30m&to=now
      crop_top: 130
ax206:
  url: http://127.0.0.1:5000/upload
```

Most of the elements are self-explanatory, the crop_top allows you to trim off the top of the dashboard that maintains
the menu system from grafana so more real-estate is available to the LCD screen.

### AX206 Image Server

The included AX206 image server provides a flask based API that allows any client the ability to publish 
