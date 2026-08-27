.. News Application documentation master file

News Application documentation
==============================

Welcome to the documentation for the **News Application**, a Django
capstone project that lets journalists write articles, editors
approve them, and readers browse approved articles and newsletters
via both a web front end and a REST API.

Overview
--------

* **Readers** can browse approved articles and newsletters, and
  subscribe to publishers or journalists.
* **Journalists** can create, update, and delete their own articles
  and compile newsletters.
* **Editors** can review and approve pending articles, which
  triggers email notifications to subscribers and posts the article
  to the internal API.

See the ``README.md`` file in the project root for setup
instructions covering both a local ``venv`` install and Docker.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   modules
