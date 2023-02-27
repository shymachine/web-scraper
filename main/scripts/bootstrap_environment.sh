#!/bin/bash

source environment_variables.sh

echo "Step 1: Installing 'virtualenv'..."
pip install --user virtualenv
echo "...done"


echo "Step 2: Creating the virtualenv for 'WebScraper'..."
mkdir -p "${VIRTUALENV_DIR}"
pushd "${VIRTUALENV_DIR}"
python -m venv "${VIRTUALENV_NAME}"
popd
echo "...done"


echo "Step 3: Installing all site-packages in the 'WebScraper' virtualenv..."
source "${VIRTUALENV_LOCATION}\Scripts\activate"
pip install -r "${BASE_DIR}/requirements.txt"
echo "...done"

echo "All Steps completed successfully."

echo "Press any key to continue"
while [ true ] ; do
read -t 3 -n 1
if [ $? = 0 ] ; then
exit ;
else
echo "waiting for the keypress"
fi
done
