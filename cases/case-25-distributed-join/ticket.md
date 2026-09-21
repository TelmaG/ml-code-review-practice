# PR: Distributed training join

Context: 8TB clickstream joins 40TB catalog data on a 200-node cluster. The job must complete in 2 hours without driver OOM or severe partition skew.