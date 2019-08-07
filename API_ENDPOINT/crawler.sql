CREATE TABLE dt_company(
    id_company INT NOT NULL DEFAULT unique_rowid(),
    nm_company STRING(200) NULL,
    url_company STRING(200) NULL,
    currency_used STRING(200) NULL,
    CONSTRAINT "primary" PRIMARY KEY (id_company ASC),
    UNIQUE INDEX company_company_name_key (nm_company ASC),
    FAMILY "primary" (id_company, nm_company, url_company, currency_used)
);

CREATE TABLE dt_product(
    id_product INT NOT NULL DEFAULT unique_rowid(),
    nm_product STRING(200) NULL,
    nm_databaseRef STRING(200) NULL,
    CONSTRAINT "primary" PRIMARY KEY (id_product ASC),
    UNIQUE INDEX product_product_name_key (nm_product ASC),
    FAMILY "primary" (id_product, nm_product, nm_databaseRef)
);

CREATE TABLE dt_company_product(
    id_company_product INT NOT NULL DEFAULT unique_rowid(),
    id_product INT NULL,
    id_company INT NULL,
    id_worker INT NULL,
    id_conf INT NULL,
    nm_company_product STRING(200) NULL,
    status_page STRING(200) NULL,
    status_scraper STRING(200) NULL,
    CONSTRAINT "primary" PRIMARY KEY (id_company_product ASC),
    UNIQUE INDEX company_product_company_product_name_key(nm_company_product ASC),
    INDEX product_auto_index_fk_id_product_ref_product (id_product ASC),
    INDEX company_auto_index_fk_id_company_ref_company (id_company ASC),
    INDEX worker_auto_index_fk_id_worker_ref_worker (id_worker ASC),
    INDEX conf_auto_index_fk_id_conf_ref_conf (id_conf ASC),
    FAMILY "primary" (id_company_product, id_product, id_company, id_worker,status_page,status_scraper)
);

CREATE TABLE dt_worker(
    id_worker INT NOT NULL DEFAULT unique_rowid(),
    loc_schedule_config STRING(200) NULL,
    loc_config STRING(200) NULL,
    status_worker STRING(200) NULL,
    CONSTRAINT "primary" PRIMARY KEY (id_worker ASC),
    UNIQUE INDEX worker_loc_schedule_config (loc_schedule_config ASC),
    UNIQUE INDEX worker_loc_config (loc_config ASC),
    FAMILY "primary" (id_worker, loc_schedule_config, loc_config)
    );

CREATE TABLE dt_vm(
    id_vm INT NOT NULL DEFAULT unique_rowid(),
    id_company_product INT NOT NULL,
    spec_vcpu STRING(200) NULL,
    spec_clock STRING(200) NULL,
    spec_ram STRING(200) NULL,
    spec_os STRING(200) NULL,
    spec_storage_volume STRING(200) NULL,
    spec_ssd_volume STRING(200) NULL,
    spec_snapshot_volume STRING(200) NULL,
    spec_template_volume STRING(200) NULL,
    spec_iso_volume STRING(200) NULL,
    spec_public_ip STRING(200) NULL,
    spec_backup_storage STRING(200) NULL,
    spec_price STRING(200) NULL,
    spec_notes STRING(200) NULL,
    date_time STRING(200) NULL,
    CONSTRAINT dt_vm_pk PRIMARY KEY (id_vm ASC),
    INDEX company_product_auto_index_fk_id_company_product_ref_company_product (id_company_product ASC),
    FAMILY "primary" (id_vm ,id_company_product, spec_vCPU, spec_clock, spec_RAM, spec_OS, spec_Storage_Volume, spec_SSD_Volume, spec_Snapshot_Volume, spec_Template_Volume, spec_ISO_Volume, spec_Public_IP, spec_Backup_Storage, spec_price, spec_notes, date_time)
);


CREATE TABLE dt_additional_features(
    id_additional_features INT NOT NULL DEFAULT unique_rowid(),
    id_company_product INT NOT NULL,
    spec_features STRING(200) NULL,
    spec_features_value STRING(200) NULL,
    spec_features_price STRING(200) NULL,
    CONSTRAINT dt_additional_features_pk PRIMARY KEY (id_additional_features ASC),
    INDEX company_product_auto_index_fk_id_company_product_ref_company_product (id_company_product ASC),
    FAMILY "primary" (id_additional_features,id_company_product,spec_features,spec_features_value,spec_features_price)
);

CREATE TABLE dt_domain_type(
    id_domain_type INT NOT NULL DEFAULT unique_rowid(),
    nm_domain_type STRING(200),
    CONSTRAINT dt_domain_type_pk PRIMARY KEY (id_domain_type ASC),
    FAMILY "primary" (id_domain_type)
);

CREATE TABLE dt_domain(
    id_domain INT NOT NULL DEFAULT unique_rowid(),
    id_company_product INT NOT NULL,
    id_domain_type INT NOT NULL,
    spec_price STRING(200) NULL,
    date_time STRING(200) NULL,
    CONSTRAINT id_domain_pk PRIMARY KEY (id_domain ASC),
    INDEX company_product_auto_index_fk_id_company_product_ref_company_product(id_company_product ASC),
    INDEX domain_type_auto_index_fk_id_domain_type_ref_domain_type(id_domain_type ASC),
    FAMILY "primary" (id_domain, id_company_product, id_domain_type)
);

CREATE TABLE dt_hosting(
    id_hosting INT NOT NULL DEFAULT unique_rowid(),
    id_company_product INT NOT NULL,
    spec_price STRING(200) NULL,
    spec_storage STRING(200) NULL,
    spec_database STRING(200) NULL,
    spec_free_domain STRING(200) NULL,
    spec_hosting_domain STRING(200) NULL,
    spec_subdomain STRING(200) NULL,
    spec_ftp_user STRING(200) NULL,
    spec_control_panel STRING(200) NULL,
    spec_email_account STRING(200) NULL,
    spec_spam_filter STRING(200) NULL,
    date_time STRING(200) NULL,
    CONSTRAINT dt_hosting PRIMARY KEY (id_hosting ASC),
    INDEX company_product_auto_index_fk_id_company_product_ref_company_product (id_company_product ASC),
    FAMILY "primary" (id_hosting, id_company_product, spec_price, spec_storage, spec_database, spec_free_domain, spec_hosting_domain, spec_subdomain, spec_ftp_user, spec_control_panel, spec_email_account, spec_spam_filter, date_time)
);

CREATE TABLE dt_config(
    id_conf INT NOT NULL DEFAULT unique_rowid(),
    conf_nm STRING(200) NULL,
    date_time STRING(200) NULL,
    CONSTRAINT dt_hosting PRIMARY KEY (id_conf ASC),
    FAMILY "primary" (id_conf)
);

ALTER TABLE dt_company_product ADD CONSTRAINT product_auto_index_fk_id_product_ref_product FOREIGN KEY (id_product) REFERENCES dt_product (id_product) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE dt_company_product ADD CONSTRAINT company_auto_index_fk_id_company_ref_company FOREIGN KEY (id_company) REFERENCES dt_company (id_company) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE dt_company_product ADD CONSTRAINT worker_auto_index_fk_id_worker_ref_worker FOREIGN KEY (id_worker) REFERENCES dt_worker (id_worker) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE dt_company_product ADD CONSTRAINT conf_auto_index_fk_id_conf_ref_conf FOREIGN KEY (id_conf) REFERENCES dt_config(id_conf) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE dt_vm ADD CONSTRAINT company_product_auto_index_fk_id_company_product_ref_company_product FOREIGN KEY (id_company_product) REFERENCES dt_company_product (id_company_product) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE dt_additional_features ADD CONSTRAINT company_product_auto_index_fk_id_company_product_ref_company_product FOREIGN KEY (id_company_product) REFERENCES dt_company_product(id_company_product) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE dt_hosting ADD CONSTRAINT company_product_auto_index_fk_id_company_product_ref_company_product FOREIGN KEY (id_company_product) REFERENCES dt_company_product (id_company_product) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE dt_domain ADD CONSTRAINT company_product_auto_index_fk_id_company_product_ref_company_product FOREIGN KEY (id_company_product) REFERENCES dt_company_product (id_company_product) ON DELETE CASCADE ON UPDATE CASCADE;
ALTER TABLE dt_domain ADD CONSTRAINT domain_type_auto_index_fk_id_domain_type_ref_domain_type FOREIGN KEY (id_domain_type) REFERENCES dt_domain_type (id_domain_type) ON DELETE CASCADE ON UPDATE CASCADE;


CREATE VIEW v_product_vm (id_company,id_company_product,id_product,id_vm,id_additional_features,nm_company,url_company,nm_company_product,nm_product,currency_used,spec_vcpu,spec_clock,spec_ram,spec_os,spec_storage_volume,spec_ssd_volume,spec_snapshot_volume,spec_template_volume,spec_iso_volume,spec_public_ip,spec_backup_storage,spec_features,spec_features_value,spec_features_price,spec_price,date_time)
AS SELECT m1.id_company, m3.id_company_product,m2.id_product, m4.id_vm, m5.id_additional_features, m1.nm_company, m1.url_company, m3.nm_company_product, m2.nm_product, m1.currency_used,  m4.spec_vcpu, m4.spec_clock,m4.spec_ram, m4.spec_os, m4.spec_storage_volume, m4.spec_ssd_volume, m4.spec_snapshot_volume, m4.spec_template_volume, m4.spec_iso_volume, m4.spec_public_ip, m4.spec_backup_storage,m5.spec_features,m5.spec_features_value,m5.spec_features_price,m4.spec_price,m4.date_time
FROM public.dt_vm AS m4 JOIN public.dt_company_product as m3 ON m4.id_company_product = m3.id_company_product JOIN public.dt_product as m2 on m3.id_product = m2.id_product JOIN public.dt_company as m1 on m3.id_company = m1.id_company JOIN public.dt_additional_features as m5 on m3.id_company_product = m5.id_company_product;

CREATE VIEW v_product_hosting (id_company,id_company_product,id_product,id_hosting,id_additional_features,nm_company,url_company,nm_product,nm_company_product,currency_used,spec_storage,spec_database,spec_free_domain,spec_hosting_domain,spec_subdomain,spec_ftp_user,spec_control_panel,spec_email_account,spec_spam_filter,date_time,spec_features,spec_features_value,spec_features_price,spec_price) 
AS SELECT m1.id_company,m3.id_company_product,m2.id_product,m4.id_hosting,m5.id_additional_features,m1.nm_company,m1.url_company,m2.nm_product,m3.nm_company_product,m1.currency_used,m4.spec_storage,m4.spec_database,m4.spec_free_domain,m4.spec_hosting_domain,m4.spec_subdomain,m4.spec_ftp_user,m4.spec_control_panel,m4.spec_email_account,m4.spec_spam_filter,m4.date_time,m5.spec_features,m5.spec_features_value,m5.spec_features_price,m4.spec_price 
FROM public.dt_hosting as m4 JOIN public.dt_company_product AS m3 on m4.id_company_product = m3.id_company_product JOIN public.dt_product as m2 on m3.id_product = m2.id_product JOIN public.dt_company as m1 on m3.id_company = m1.id_company JOIN public.dt_additional_features as m5 on m3.id_company_product = m5.id_company_product;

CREATE VIEW v_domain (id_company,id_company_product,id_product,id_domain_type,id_domain,nm_domain_type,spec_price,date_time) 
AS SELECT m1.id_company,m3.id_company_product,m2.id_product,m4.id_domain_type,m5.id_domain,m4.nm_domain_type,m5.spec_price,m5.date_time
FROM public.dt_domain as m5 JOIN public.dt_company_product AS m3 on m5.id_company_product = m3.id_company_product JOIN public.dt_product as m2 on m3.id_product = m2.id_product JOIN public.dt_company as m1 on m3.id_company = m1.id_company JOIN public.dt_domain_type as m4 on m5.id_domain_type = m4.id_domain_type;

INSERT INTO dt_product(id_product, nm_product, nm_databaseRef) VALUES
(402140280385142785, 'vm', 'dt_vm'),
(402393625286410241, 'hosting', 'dt_hosting'),
(474892890585694209, 'domain' ,' dt_domain');

INSERT INTO dt_domain_type(id_domain_type,nm_domain_type) VALUES
(474894616865964033, '.id'),
(474894697301409793, '.com'),
(474894724220780545, '.xyz'),
(474894755499540481, '.net'),
(474894783920504833, '.org'),
(474894818444443649, '.co.id'),
(474894861517553665, '.web.id'),
(474894891970166785, '.my.id'),
(474894926867595265, '.biz.id'),
(474894951916109825, '.ac.id'),
(474894979768647681, '.sch.id'),
(474895007257067521, '.biz'),
(474895027987152897, '.co'),
(474895039157043201, '.tv'),
(474895067465973761, '.io'),
(474895076807016449, '.info');

INSERT INTO dt_worker(id_worker, loc_schedule_config, loc_config) VALUES
(402140815780249601, 'test_worker_schedule', 'test_worker_config');


-- CREATE VIEW v_product_vm_test (id_company,id_company_product,id_product,id_vm,id_additional_features,nm_company,url_company,nm_company_product,nm_product,currency_used,spec_vCPU,spec_clock,spec_RAM,spec_OS,spec_Storage_Volume,spec_SSD_Volume,spec_Snapshot_Volume,spec_Template_Volume,spec_ISO_Volume,spec_Public_IP,spec_Backup_Storage,spec_features,spec_features_price,spec_price,date_time)
-- AS SELECT m4.id_company, m3.id_company_product,m5.id_additional_features, m2.id_product, m1.id_vm, m4.nm_company, m4.url_company, m3.nm_company_product, m2.nm_product, m4.currency_used, m1.spec_price, m1.spec_vCPU, m1.spec_clock,m1.spec_RAM, m1.spec_OS, m1.spec_Storage_Volume, m1.spec_SSD_Volume, m1.spec_Snapshot_Volume, m1.spec_Template_Volume, m1.spec_ISO_Volume, m1.spec_Public_IP, m1.spec_Backup_Storage,m5.spec_features,m5.spec_features_price,m1.date_time
-- FROM public.dt_vm AS m1 JOIN public.dt_company_product as m3 ON m1.id_company_product = m3.id_company_product JOIN public.dt_product as m2 on m3.id_product = m2.id_product JOIN public.dt_company as m4 on m3.id_company = m4.id_company JOIN public.dt_additional_features as m5 on m5.id_company_product = m3.id_company_product;
