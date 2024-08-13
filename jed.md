
# Jira Upgrade and PostgreSQL Migration Plan

## Pre-Migration Assessment and Planning

### Initial Assessment and Documentation
- **Current State Analysis**: Document the current Jira setup, including the version, plugins, customizations, database configurations, and integrations. Identify any dependencies or interconnections with other systems, such as CI/CD pipelines, reporting tools, or data warehouses.
- **Vulnerability Analysis**: Review specific vulnerabilities identified by the security team, particularly those related to the current Jira version (8.x) and PostgreSQL database. Cross-reference these vulnerabilities with known CVEs (Common Vulnerabilities and Exposures) to understand their impact and severity.

### Engage Key Stakeholders
- **Security Team**: Collaborate with the security team to ensure all identified vulnerabilities are addressed in the upgrade plan. Discuss implementing additional security measures, such as IP whitelisting, enhanced logging, and audit trails post-upgrade.
- **Infrastructure Team**: Discuss the current infrastructure setup, including server specifications, resource utilization, and cost considerations. Consider using containerization (e.g., Docker) or orchestration tools (e.g., Kubernetes) for better resource management and scalability.

### Upgrade Requirements Gathering
- **Compatibility Checks**: Identify all third-party plugins and custom integrations, ensuring their compatibility with Jira 9.12 or 9.17. Use Atlassian's compatibility matrix and reach out to vendors for any updates or patches required.
- **PostgreSQL Upgrade Path**: Determine the necessary steps to upgrade PostgreSQL to a secure and supported version. This might involve transitioning from PostgreSQL 9.x or 10.x to the latest stable release, which supports advanced features such as parallel query processing and enhanced JSON support.

### Develop a Detailed Migration Plan
- **Backup Strategy**: Plan a comprehensive backup strategy, including full backups of the Jira database, configurations, and application files. Ensure that backups are stored securely and are easily accessible in case a rollback is required.
- **Staging Environment Setup**: Create a staging environment that mirrors the production setup for testing. This environment should replicate the same hardware configurations, network settings, and data volume to identify potential performance issues.
- **Test Plan**:
  - **Functional Testing**: Ensure all Jira functionalities, especially those related to model metadata tracking, work as expected. This includes testing Jira's REST API endpoints to verify that data retrieval and updates are functioning correctly.
  - **Integration Testing**: Test all integrations with external systems, including any webhook-based integrations or data exports to other systems (e.g., BI tools or ETL processes).
  - **Security Testing**: Perform vulnerability scans in the staging environment post-upgrade using tools like OWASP ZAP, Nessus, or custom scripts. Conduct penetration testing to ensure there are no exploitable vulnerabilities.
  - **Reindexing Test**: Given the requirement for a full reindex during the upgrade, simulate this process in the staging environment to estimate the time required and identify any performance bottlenecks.

---

## Major Changes and Technical Issues in Upgrading Jira from 8.20.x to 9.12/17

### Major Changes
- **End of Support for Server Licenses**: Jira 9.12 is the last version that supports server licenses, with support ending on February 15, 2024. Future updates will only be available for Data Center versions, which may require organizations to consider migrating to Atlassian Cloud or Data Center.
- **Reindexing Requirement**: Upgrading from Jira 8.x to 9.x triggers a full reindex, which can cause significant downtime. It's crucial to plan this upgrade during a low-activity period to minimize disruptions.
- **Database Structure Changes**: The upgrade introduces new database structures, such as new `_version` tables (e.g., `worklog_version`, `issue_version`, `comment_version`). Missing records in these tables need to be inserted manually during the upgrade process.
- **Updated Apache Tomcat**: The Apache Tomcat version is upgraded in Jira 9.10 to 9.0.75, which is not compatible with older New Relic agents (versions prior to 8.2.0). This update might necessitate an upgrade to your monitoring tools.
- **Automation Enhancements**: Jira 9.11 introduced significant enhancements to automation, including the "Look up issues" and "Create variable" actions, masking secret keys in automation rules, and enabling an allowlist for outbound HTTP requests by default.

### Potential Technical Issues
- **Plugin and Customization Compatibility**: Many third-party plugins and customizations may not be immediately compatible with Jira 9.x. Testing in a staging environment before upgrading is essential to identify and mitigate these issues.
- **Security Configuration Adjustments**: Post-upgrade, there may be a need to adjust security settings, such as reconfiguring SSL/TLS, updating authentication methods, or enabling new security features that weren't available in earlier versions.
- **Performance Impact During Reindexing**: The reindexing process can be resource-intensive, potentially affecting performance or causing system instability during the upgrade.
- **Data Integrity Checks**: Given the database changes, it's critical to perform thorough data integrity checks before and after the upgrade to ensure that all data has been migrated correctly and that no records have been lost or corrupted.
- **Increased Resource Requirements**: The new features and enhancements in Jira 9.x may require more system resources, such as CPU, memory, and storage. This might necessitate hardware upgrades or cloud resource scaling to maintain performance.

---

## Questions to Ask the Jira Infrastructure Team

### Regarding the Upgrade Process
- What is the current resource utilization of the Jira instances, and are there any opportunities for cost savings through optimization?
- What is the expected downtime for the upgrade, and how can it be minimized? Can we leverage blue-green deployment strategies to reduce downtime?
- Are there any known issues or challenges from past upgrades that we should be aware of? How will they be mitigated during this upgrade?
- What is the fallback plan if the upgrade encounters critical issues? How quickly can we revert to the previous version, and what data or configurations might be lost in the process?
- What steps are being taken to ensure data consistency and integrity during the upgrade process? Will there be a need for data validation post-upgrade?
- How will the full reindexing process be managed, and what is the estimated time required? Can the reindexing be broken into phases to reduce downtime?
- How will we handle the potential performance impact during reindexing, and are there any optimization steps we can take to minimize this impact?

### For PostgreSQL Upgrade
- What version of PostgreSQL is currently running, and what are the specific vulnerabilities associated with it? Are we considering a major version upgrade (e.g., from 9.x to 13.x), and what are the implications of such an upgrade?
- What steps are required to upgrade PostgreSQL, and how will this impact Jira’s performance during and after the migration? Will the upgrade process involve data migration or schema changes that require extensive testing?
- How will we handle the potential downtime or performance degradation during the PostgreSQL upgrade? Is there an opportunity to perform a rolling upgrade or implement a high-availability setup to minimize impact?
- What are the post-upgrade tasks specific to PostgreSQL? For example, will we need to reindex tables, update configurations, or tune performance settings to align with the new version?
- How will the new PostgreSQL version handle the increased load from Jira 9.x, and are there any optimizations needed to ensure optimal performance?

### On Security Enhancements
- What specific security features will be enabled or enhanced in Jira 9.x to mitigate the vulnerabilities identified? Are there plans to implement enhanced encryption for data at rest and in transit?
- How will the security configurations, such as SSL/TLS and authentication methods, be managed post-upgrade? Will we be implementing multi-factor authentication (MFA) or integrating with SSO providers?
- What are the ongoing security practices post-upgrade? For example, how will security patches be applied in the future, and will we set up regular vulnerability assessments?
- Are there any specific compliance requirements that need to be addressed post-upgrade, and how will they be implemented?

### About Monitoring and Maintenance
- What monitoring tools are currently in place, and how will they be affected by the upgrade? Will we integrate with existing monitoring solutions like Prometheus, Grafana, or Datadog?
- How do we plan to handle ongoing maintenance and patches to prevent future vulnerabilities? Can we automate patch management and security updates using CI/CD pipelines?
- What is the process for monitoring and responding to performance issues post-upgrade? Will there be specific thresholds or alerts set up to ensure that any degradation in performance is addressed promptly?
- How are we planning to monitor the health and performance of the PostgreSQL database post-upgrade? Are there specific tools or scripts in place for proactive monitoring and alerting?
