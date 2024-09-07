# Copyright 2024 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import os
import pytest
from .utils import *

FIXTURES_DIR = os.path.join(os.path.dirname(__file__), "../../samples/x-non-vpc-peering")

@pytest.fixture(scope="module")
def resources(recursive_plan_runner):
    _, resources = recursive_plan_runner(
        FIXTURES_DIR,
        tf_var_file=os.path.join(FIXTURES_DIR, "x-demo.tfvars"),
        project_id="testonly",
        project_create="true"
    )
    return resources

def test_resource_count(resources):
    "Test total number of resources created."
    assert len(resources) == 32
    
def test_apigee_instance(resources):
    "Test Apigee Instance Resource"
    assert_instance(resources, "us-west1", ip_range=None) # Not providing the ip_range as it dynamic/internal for non-vpc peering setup.
    
def test_apigee_instance_attachment(resources):
    "Test Apigee Instance Attachments."
    assert_instance_attachment(resources, ["us-west1-test1", "us-west1-test2"])
    
def test_envgroup_attachment(resources):
    "Test Apigee Envgroup Attachments."
    assert_envgroup_attachment(resources, ["test1", "test2"])

def test_envgroup(resources):
    "Test env group."
    assert_envgroup_name(resources, "test")
    
def test_vpcs(resources):
    "Test that there is one VPC for PSC NEG"
    attachments = [
        r["values"]
        for r in resources
        if r["type"] == "google_compute_network"
    ]
    assert len(attachments) == 1
    assert set(a["name"] for a in attachments) == set(["psc-ingress-vpc"])
    
def test_same_region(resources):
    "Test that Apigee instance and the NEG are in the same region."
    instances = [
        r for r in resources if r["type"] == "google_apigee_instance"
    ]
    negs = [
        r for r in resources if r["type"] == "google_compute_region_network_endpoint_group"
    ]
    assert len(instances) == 1
    assert len(negs) == 1
    assert instances[0]["values"]["location"] == negs[0]["values"]["region"]