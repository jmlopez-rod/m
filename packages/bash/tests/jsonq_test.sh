#!/bin/bash

testGetSingleByName() {
  val=$(m jsonq @fixtures/jsonq.json name)
  assertEquals "name prop" "m" "$val"

  val=$(m jsonq @fixtures/jsonq.json array.3)
  assertEquals "4th value" "4.5" "$val"

  val=$(m jsonq @fixtures/jsonq.json dict.color)
  assertEquals "dict.color" "#ff0000" "$val"

  val=$(m jsonq @fixtures/jsonq.json dict.circle.center.0)
  assertEquals "center.x" "2" "$val"
}

testGetSingleByRedirect() {
  val=$(m jsonq name < fixtures/jsonq.json)
  assertEquals "name prop" "m" "$val"

  val=$(m jsonq array.3 < fixtures/jsonq.json)
  assertEquals "4th value" "4.5" "$val"

  val=$(m jsonq dict.color < fixtures/jsonq.json)
  assertEquals "dict.color" "#ff0000" "$val"

  val=$(m jsonq dict.circle.center.0 < fixtures/jsonq.json)
  assertEquals "center.x" "2" "$val"
}

testGetSingleByPipe() {
  val=$(cat fixtures/jsonq.json | m jsonq name)
  assertEquals "name prop" "m" "$val"

  val=$(cat fixtures/jsonq.json | m jsonq array.3)
  assertEquals "4th value" "4.5" "$val"

  val=$(cat fixtures/jsonq.json | m jsonq dict.color)
  assertEquals "dict.color" "#ff0000" "$val"

  val=$(cat fixtures/jsonq.json | m jsonq dict.circle.center.0)
  assertEquals "center.x" "2" "$val"
}

testGetMulipleValues() {
  read -r -d '\n' \
    name centerY \
    <<< "$(m jsonq @fixtures/jsonq.json name dict.circle.center.1)"
  assertEquals "name prop" "m" "$name"
  assertEquals "height" "3" "$centerY"
}

. ./shunit2.sh
