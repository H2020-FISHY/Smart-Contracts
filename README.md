# FISHY Smart Contracts Component

This is the Smart Contarcts Component of the H2020 FISHY Platform. Its main puprose is to ensure the integrity of the data written in the Central Repository, pushed by the rest of the FISHY components.

The project consists of two sub-components:

* The [Smart Contracts Server](./server/README.md) which is responsible for receiving and storing the FISHY events/reports in IPFS and the information to retrieve them from private IPFS in a private Quorum network (check [DAPP](./dapp/README.md)). 
* The [DAPP component](./dapp/README.md), which is the private blockchain network used by the Server component to store the necessary information to retrieve the FISHY events/reports from private IPFS.  