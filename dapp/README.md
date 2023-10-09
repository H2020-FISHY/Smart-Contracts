# DAPP

The DAPP sub-component of the FISHY Smart Contract component.

## Description
The DAPP component of the FISHY Smart Contract component is a Helm chart responsible for deploying the nodes of a Quorum network and the Smart Contracts we want to access. The present Helm Chart is developed by Synelixis.

This chart can used to make a deployment of Quorum in the FRF.

## Installation
To install the Helm chart, run the following:
```bash
helm install quorum charts/quorum -f charts/quorum/values.yaml 
```

To upgrade the chart, run the following:
```bash
helm upgrade --reuse-values quorum -f charts/quorum/values.yaml charts/quorum
```

To delete the chart, run the following:
```bash
helm delete quorum  
```