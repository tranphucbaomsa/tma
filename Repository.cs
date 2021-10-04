namespace PurchaseOrders
{
    using System;
    using System.Collections.Generic;
    using System.Data;
    using System.Data.SqlClient;
    using System.Linq;
    using Orders;
    using Outlets;
    using Suppliers;

    /// <summary>
    /// Summary description for Repository
    /// </summary>
    public class Repository
    {
        #region Methods
        /// <summary>
        /// Gets the header data for a PO
        /// </summary>
        /// <param name="id"></param>
        /// <returns></returns>
        public Header GetHeader(int id)
        {
            string queryText = @"
                SELECT  DeliverTo,
                        ISNULL(SentDate, dbo.GetSydneyDate()) as DateSent,
                        SupplierComments,
                        WarehouseComments
                FROM    PO
                WHERE   POID = @POID

                SELECT  s.Supplier_ID,
                        s.Supplier_Code,
                        s.Street_Address,
                        s.Supplier,
                        s.Suburb,
                        s.State,
                        s.Post_Code,
                        s.Comments
                FROM    PO
                        INNER JOIN Suppliers s ON PO.Supplier_ID = s.Supplier_Code
                WHERE   PO.POID = @POID

                ;WITH Settings 
                AS (
	                SELECT	CompanySiteName, CompanySiteAddressLine1, CompanySiteAddressLine2, CompanySiteSuburb, CompanySiteState, 
			                CompanySitePostcode, CustomerServicePhone, CustomerServiceFax, CustomerServiceEmail, CompanySiteABN, CompanyNumberLabel
	                FROM
	                (
		                SELECT	Name, Value 
		                FROM	setting 
		                WHERE	Name = 'CompanySiteName' or Name = 'CompanySiteAddressLine1' or Name = 'CompanySiteAddressLine2' or Name = 'CompanySiteSuburb' or 
				                Name = 'CompanySiteState' or Name = 'CompanySitePostcode' or  Name = 'CustomerServicePhone' or Name = 'CustomerServiceFax' or 
				                Name = 'CustomerServiceEmail' or Name = 'CompanySiteABN' or Name = 'CompanyNumberLabel') AS source
	                PIVOT
	                (
	                 MIN(Value)
	                 FOR [Name] IN (CompanySiteName, CompanySiteAddressLine1, CompanySiteAddressLine2, CompanySiteSuburb, CompanySiteState, 
					                CompanySitePostcode, CustomerServicePhone, CustomerServiceFax, CustomerServiceEmail, CompanySiteABN, CompanyNumberLabel)
	                ) AS PIVOTOutput
                )

                SELECT  w.WHID,
                        w.WarehouseName,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.Company ELSE Settings.CompanySiteName END AS Company,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.Address ELSE Settings.CompanySiteAddressLine1 END AS Address,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.Address2 ELSE Settings.CompanySiteAddressLine2 END AS Address2,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.Address3 ELSE '' END AS Address3,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.Suburb ELSE Settings.CompanySiteSuburb END AS Suburb,                        
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.State ELSE Settings.CompanySiteState END AS State,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.PCode ELSE Settings.CompanySitePostcode END AS PCode,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.Phone ELSE Settings.CustomerServicePhone END AS Phone,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.Fax ELSE Settings.CustomerServiceFax END AS Fax,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.Email ELSE Settings.CustomerServiceEmail END AS Email,
                        CASE WHEN w.useAddressOnInvoice = 1 THEN w.ABN ELSE Settings.CompanySiteABN END AS ABN,
						CASE WHEN w.useAddressOnInvoice = 1 THEN ISNULL(w.CompanyNumberLabel, 'ABN') ELSE Settings.CompanyNumberLabel END AS CompanyNumberLabel,
                        w.useAddressOnInvoice
                FROM    PO
                        INNER JOIN POWHID pw ON PO.POID = pw.POID
                        INNER JOIN Warehouse w ON pw.WHID = w.WHID
						CROSS JOIN Settings
                WHERE   PO.POID = @POID

                SELECT  o.Order_ID,
                        o.OrderNumber,
                        o.Del_Name,
                        o.Del_Address,
                        o.Del_Address2,
                        o.Del_State,
                        o.Del_PostCode,
                        o.Del_Suburb,
                        o.Del_Phone,
                        o.Public_Comments
                FROM    PO
                        INNER JOIN Orders o on o.Order_ID = po.Order_ID 
                WHERE PO.POID = @POID

                SELECT 
                    CASE WHEN ISNULL(PO.DateOriginalETD,'')='' THEN '' 
						    ELSE FORMAT (PO.DateOriginalETD, 'dd MMMM yyyy') 
					    END AS DateOriginalETD,
					CASE WHEN ISNULL((SELECT spt3.FieldName FROM SupplierPOTemplate spt3
										WHERE spt3.SupplierId = s.Supplier_ID
											AND spt3.[Type]='AdditionalFields' 
											AND spt3.FieldName='OriginalDateOfDeparture'), '') = '' THEN 0
							ELSE 1
						END as OriginalDateOfDeparture
	            FROM    PO
		            INNER JOIN Suppliers s ON PO.Supplier_ID = s.Supplier_Code
	            WHERE   PO.POID = @POID
";
            DataSet dsHeaderData = Db.ExecuteDataSet(queryText,
                                                     new List<SqlParameter>
                                                     {
                                                         new SqlParameter("@POID",
                                                                          id)
                                                     },
                                                     CommandType.Text);
            if (dsHeaderData.Tables.Count == 0 ||
                dsHeaderData.Tables[0]
                            .Rows.Count ==
                0)
            {
                throw new ArgumentException($"Purchase Order {id} not found");
            }

            DataRow dataRow = dsHeaderData.Tables[0]
                                          .Rows[0];
            Header header = new Header
            {
                DeliverTo = dataRow["DeliverTo"]
                                   .ToString(),
                DateSent = (DateTime)dataRow["DateSent"],
                OutletComments = dataRow["WarehouseComments"]
                                   .ToString(),
                SupplierComments = dataRow["SupplierComments"]
                                   .ToString()
            };

            dataRow = dsHeaderData.Tables[1]
                                  .Rows[0];

            header.Supplier = new Supplier
            {
                Id = (int)dataRow["Supplier_ID"],
                Code = dataRow["Supplier_Code"]
                                     .ToString(),
                Name = dataRow["Supplier"]
                                     .ToString(),
                Comments = dataRow["Comments"]
                                     .ToString(),
                Address = new Address
                {
                    Line1 = dataRow["Street_Address"]
                                                   .ToString(),
                    Suburb = dataRow["Suburb"]
                                                   .ToString(),
                    State = dataRow["State"]
                                                   .ToString(),
                    Postcode = dataRow["Post_Code"]
                                                   .ToString()
                }
            };

            dataRow = dsHeaderData.Tables[2]
                                  .Rows[0];

            header.Outlet = new Outlet
            {
                Id = (int)dataRow["WHID"],
                Name = dataRow["WarehouseName"]
                                   .ToString(),
                CompanyName = dataRow["Company"]
                                   .ToString(),
                CompanyNumberLabel = dataRow["CompanyNumberLabel"]
                                   .ToString(),
                CompanyNumber = dataRow["ABN"]
                                   .ToString(),
                UseAddressOnInvoice = (bool)dataRow["useAddressOnInvoice"],
                Address = new Address
                {
                    Line1 = dataRow["Address"]
                                                 .ToString(),
                    Line2 = dataRow["Address2"]
                                                 .ToString(),
                    Line3 = dataRow["Address3"]
                                                 .ToString(),
                    Suburb = dataRow["Suburb"]
                                                 .ToString(),
                    State = dataRow["State"]
                                                 .ToString(),
                    Postcode = dataRow["PCode"]
                                                 .ToString(),
                    PhoneNumber = dataRow["Phone"]
                                                 .ToString(),
                    EmailAddress = dataRow["Email"]
                                                 .ToString(),
                    FaxNumber = dataRow["Fax"]
                                                 .ToString()
                }
            };

            if (dsHeaderData.Tables[3]
                            .Rows.Count >
                0)
            {
                dataRow = dsHeaderData.Tables[3]
                                      .Rows[0];
                header.Order = new Order
                {
                    Id = (int)dataRow["Order_ID"],
                    Number = dataRow["OrderNumber"]
                                      .ToString(),
                    PublicComments = dataRow["Public_Comments"]
                                      .ToString(),
                    DeliveryName = dataRow["Del_Name"]
                                      .ToString(),
                    DeliveryAddress = new Address
                    {
                        Line1 = dataRow["Del_Address"]
                                                            .ToString(),
                        Line2 = dataRow["Del_Address2"]
                                                            .ToString(),
                        Suburb = dataRow["Del_Suburb"]
                                                            .ToString(),
                        State = dataRow["Del_State"]
                                                            .ToString(),
                        Postcode = dataRow["Del_PostCode"]
                                                            .ToString(),
                        PhoneNumber = dataRow["Del_Phone"]
                                                            .ToString()
                    }
                };
            }

            if (dsHeaderData.Tables[4]
                            .Rows.Count >
                0)
            {
                dataRow = dsHeaderData.Tables[4]
                                     .Rows[0];

                header.DateOriginalETD = dataRow["DateOriginalETD"].ToString();
                header.bOriginalDateOfDeparture = Convert.ToBoolean(dataRow["OriginalDateOfDeparture"].ToString().Equals("1") ? true : false);
            }

            return header;
        }

        /// <summary>
        /// Gets the item data for a PO
        /// </summary>
        /// <param name="id"></param>
        /// <param name="format"></param>
        /// <returns></returns>
        public Items GetItems(int id,
                              PurchaseOrder.Format format)
        {
            DataTable dtItems = Db.ExecuteDataSet(this.ItemQueryText(format),
                                                  new List<SqlParameter>
                                                  {
                                                      new SqlParameter("@POID",
                                                                       id)
                                                  },
                                                  CommandType.Text)
                                  .Tables[0];

            Items items = new Items();

            items.MatrixItems = new List<MatrixItem>();
            items.PackageItems = new List<PackageItem>();
            items.StandardItems = new List<VariantItem>();

            var dtGroupByPOItem = dtItems.AsEnumerable()
                                    .GroupBy(row => row["POItemID"].ToString()).Select(
                value =>
                new
                {
                    Key = value.Key,
                    Data = value.ToList()
                }
                );

            var listPOItemId = new List<string>();

            var listPackageComplexMatrix = dtGroupByPOItem.Where(x => x.Data.Any(y => (bool)y["IsPackageProduct"]) & x.Data.Count(y => (bool)y["IsMatrixProduct"]) > 0 & x.Data.Count(y => !(bool)y["IsMatrixProduct"]) > 0).ToList();
            listPOItemId.AddRange(listPackageComplexMatrix.Select(x => x.Key));

            var packages = dtGroupByPOItem.Where(x => x.Data.Any(y => (bool)y["IsPackageProduct"]) & !listPackageComplexMatrix.Any(y => y.Key == x.Key)).ToList();
            listPOItemId.AddRange(packages.Select(x => x.Key));
            
            packages.AddRange(listPackageComplexMatrix.Select(x => new
            {
                Key = x.Key,
                Data = x.Data.Where(y => (bool)y["IsMatrixProduct"]).ToList()
            }));
            
            packages.AddRange(listPackageComplexMatrix.Select(x => new
            {
                Key = x.Key,
                Data = x.Data.Where(y => !(bool)y["IsMatrixProduct"]).ToList()
            }));


            foreach (var package in packages)
            {
                var childProductIds = package.Data.FirstOrDefault()["ChildProductID"].ToString();
                var otherPOItems = dtGroupByPOItem.Where(x => !listPOItemId.Any(y => y == x.Key) & x.Data.All(z => (bool)z["IsMatrixProduct"]));
                foreach (var otherPOItem in otherPOItems)
                {
                    if (childProductIds.Contains(otherPOItem.Data.FirstOrDefault()["ProductProdID"].ToString() + ","))
                    {
                        package.Data.AddRange(otherPOItem.Data);
                        listPOItemId.Add(otherPOItem.Key);
                    }
                }
            }

            var listPackageGenerate = new List<string>();

            foreach (var package in packages)
            {
                var packageItems = package.Data.Where(x => (bool)x["IsPackageProduct"]).ToList();
                var individualItems = package.Data.Where(x => !(bool)x["IsPackageProduct"]).ToList();
                var isSameManSku = packageItems.GroupBy(x => x["ProductManSku"].ToString()).ToList().Count() == 1;

                var listIndividualId = new List<string>();
                var isDuplicatePackage = listPackageGenerate.Any(x => x == package.Key);

                if (isSameManSku)
                {
                    var firstPackageItem = !isDuplicatePackage;

                    foreach (var packageItem in packageItems)
                    {
                        var individualDetail = individualItems.Where(
                            x => !listIndividualId.Any(
                                y => y == x["ProductProdID"].ToString()) &&
                            x["ProductProdID"].ToString() == packageItem["ProductProdID"].ToString()
                            ).ToList();

                        listIndividualId.AddRange(individualDetail.Select(x => x["ProductProdID"].ToString()));

                        if ((bool)packageItem["IsMatrixProduct"])
                        {
                            items.MatrixItems.Add(createMatrixItem(new List<DataRow>() { packageItem }, individualDetail, firstPackageItem));
                        }
                        else
                        {
                            items.PackageItems.Add(createPackageItem(new List<DataRow>() { packageItem }, firstPackageItem));
                        }

                        firstPackageItem = false;
                    }
                }
                else
                {
                    var individualDetail = individualItems.Where(x =>
                           !listIndividualId.Any(y => y == x["ProductProdID"].ToString()) &&
                           packageItems.Any(y => x["ProductProdID"].ToString() == y["ProductProdID"].ToString())
                           ).ToList();

                    if (packageItems.Any(x => (bool)x["IsMatrixProduct"]))
                    {
                        items.MatrixItems.Add(createMatrixItem(packageItems, individualDetail, isDuplicatePackage));
                    }
                    else
                    {
                        items.PackageItems.Add(createPackageItem(packageItems, isDuplicatePackage));
                    }
                }

                listPackageGenerate.Add(package.Key);
            }

            var nonPackages = dtGroupByPOItem.Where(x => !listPOItemId.Any(y => y == x.Key));
            foreach (var nonPackage in nonPackages)
            {
                var isMatrixProduct = nonPackage.Data.Any(x => (bool)x["IsMatrixProduct"]);

                if (isMatrixProduct)
                {
                    items.MatrixItems.Add(createMatrixItem(nonPackage.Data, new List<DataRow>()));
                }
                else
                {
                    items.StandardItems.AddRange(createStandardProduct(nonPackage.Data));
                }
            }

            return items;
        }

        private MatrixItem createMatrixItem(List<DataRow> rows, List<DataRow> individualDetail, bool firstPackageItem = true)
        {
            var matrixData = new MatrixItem();
            var firstRow = rows.FirstOrDefault(x => (bool)x["IsPackageProduct"]);

            if (firstRow == null)
            {
                firstRow = rows.FirstOrDefault();
            }

            if ((bool)firstRow["IsPackageProduct"])
            {
                matrixData = new MatrixItem
                {
                    ProdID = ParseToInt(firstRow["PackageProductId"]),
                    ManSku = firstRow["PackageManSku"].ToString(),
                    Sku = firstRow["PackageSKU"].ToString(),
                    Sku2 = firstRow["PackageSKU2"].ToString(),
                    Brand = firstRow["PackageBrand"].ToString(),
                    Description = firstRow["PackageDescription"].ToString(),
                    Season = firstRow["PackageSeason"].ToString(),
                    StyleCode = firstRow["PackageManSku"].ToString(),
                    SupplierSKU = firstRow["SupplierSKU"].ToString(),
                    SupplierSKU2 = firstRow["SupplierSKU2"].ToString()
                };
            }
            else
            {
                matrixData = new MatrixItem
                {
                    ProdID = ParseToInt(firstRow["ProductProdID"]),
                    ManSku = firstRow["ProductManSku"].ToString(),
                    Sku = firstRow["ProductSKU"].ToString(),
                    Sku2 = firstRow["ProductSKU2"].ToString(),
                    Brand = firstRow["ProductBrand"].ToString(),
                    Description = firstRow["ProductDescription"].ToString(),
                    Season = firstRow["ProductSeason"].ToString(),
                    StyleCode = firstRow["StyleCode"].ToString(),
                    SupplierSKU = firstRow["SupplierSKU"].ToString(),
                    SupplierSKU2 = firstRow["SupplierSKU2"].ToString()
                };
            }

            matrixData.isDuplicate = !firstPackageItem;
            matrixData.Packages = rows.Where(row => (bool)row["IsPackageProduct"])
                                .Select(row => new
                                {
                                    Sku = row["PackageSKU"].ToString(),
                                    Sku2 = row["PackageSKU2"].ToString(),
                                    OrderQuantity = (int)row["OrderQty"],
                                    TotalBuyPrice = row["TotalBuyPrice"] == DBNull.Value ? 0 : (decimal?)row["TotalBuyPrice"],
                                    SupplierSKU = row["SupplierSKU"].ToString(),
                                    SupplierSKU2 = row["SupplierSKU2"].ToString(),
                                    ProductManSku = row["ProductManSku"].ToString()
                                })
                                    .Distinct()
                                    .OrderBy(item => item.Sku)
                                    //And then we create the Matrix Package objects
                                    .Select((pItem, index) => new PackageItem(true)
                                    {
                                        Sku = pItem.Sku,
                                        Sku2 = pItem.Sku2,
                                        OrderQuantity = pItem.OrderQuantity,
                                        TotalBuyPrice = index == 0 && firstPackageItem ? pItem.TotalBuyPrice : 0,
                                        SupplierSKU = pItem.SupplierSKU,
                                        SupplierSKU2 = pItem.SupplierSKU2,
                                        isDuplicate = index != 0 || !firstPackageItem,
                                        //Finally, packages contain variant items - these are the individual products that
                                        //the matrix comprises
                                        Items = rows.AsEnumerable()
                                                        .Where(row => row["PackageSKU"].ToString() == pItem.Sku &&
                                                                    row["PackageSKU2"].ToString() == pItem.Sku2 &&
                                                                    row["ProductManSku"].ToString() == pItem.ProductManSku)
                                                        //And we create the variant objects with the data needed for a Matrix Package Variant item
                                                        //Just the size, colour and the number of units per package
                                                        .Select(row =>
                                                        {
                                                            var variantItem = new VariantItem
                                                            {
                                                                ProdID = ParseToInt(row["ProductProdID"]),
                                                                Size = new ProductAttributeValue(row["ProductSize"].ToString(),
                                                                        row["ProductSizeId"] != DBNull.Value && (int)row["ProductSizeId"] > 0 ? row["ProductSizeListOrder"] == DBNull.Value ? null : (int?)row["ProductSizeListOrder"] : int.MaxValue),
                                                                Colour = new ProductAttributeValue(row["ProductColour"].ToString(),
                                                                        row["ProductColourId"] != DBNull.Value && (int)row["ProductColourId"] > 0 ? (int?)null : int.MaxValue),
                                                                OrderQuantity = (int?)row["Units"] ?? 0,
                                                                isDuplicate = index != 0 || !firstPackageItem
                                                            };

                                                            return variantItem;
                                                        })
                                                        .ToList()
                                    })
                            .ToList();

            matrixData.Items = rows.AsEnumerable()
                                .Where(row => !(bool)row["IsPackageProduct"])
                                //Again, we only need size, colour and units + BuyPrice. Packages don't have a buy price at this level
                                //because that is a package level value
                                .Select(row => new VariantItem
                                {
                                    Size = new ProductAttributeValue(row["ProductSize"]
                                                                                        .ToString(),
                                                                                    row["ProductSizeId"] != DBNull.Value && (int)row["ProductSizeId"] > 0 ? row["ProductSizeListOrder"] == DBNull.Value ? null : (int?)row["ProductSizeListOrder"] : int.MaxValue),
                                    Colour = new ProductAttributeValue(row["ProductColour"]
                                                                                        .ToString(),
                                                                                        row["ProductColourId"] != DBNull.Value && (int)row["ProductColourId"] > 0 ? null : (int?)int.MaxValue),
                                    OrderQuantity = row["Units"] == DBNull.Value ? 0 : (int)row["Units"],
                                    TotalBuyPrice = row["TotalBuyPrice"] == DBNull.Value ? 0 : (decimal)row["TotalBuyPrice"],
                                    isDuplicate = !firstPackageItem
                                })
                                .ToList();

            if (individualDetail.Count > 0)
            {
                matrixData.Items.AddRange(individualDetail.AsEnumerable()
                                //Again, we only need size, colour and units + BuyPrice. Packages don't have a buy price at this level
                                //because that is a package level value
                                .Select(row => new VariantItem
                                {
                                    Size = new ProductAttributeValue(row["ProductSize"]
                                                                                        .ToString(),
                                                                                    row["ProductSizeId"] != DBNull.Value && (int)row["ProductSizeId"] > 0 ? row["ProductSizeListOrder"] == DBNull.Value ? null : (int?)row["ProductSizeListOrder"] : int.MaxValue),
                                    Colour = new ProductAttributeValue(row["ProductColour"]
                                                                                        .ToString(),
                                                                                        row["ProductColourId"] != DBNull.Value && (int)row["ProductColourId"] > 0 ? null : (int?)int.MaxValue),
                                    OrderQuantity = row["Units"] == DBNull.Value ? 0 : (int)row["Units"],
                                    TotalBuyPrice = row["TotalBuyPrice"] == DBNull.Value ? 0 : (decimal)row["TotalBuyPrice"]
                                })
                                .ToList());
            }

            return matrixData;
        }

        private PackageItem createPackageItem(List<DataRow> rows, bool firstPackageItem = true)
        {
            var firstPackageData = rows.FirstOrDefault();

            var packageData = new PackageItem(false)
            {
                ProdID = ParseToInt(firstPackageData["PackageProductId"]),
                ManSku = firstPackageData["PackageManSku"].ToString(),
                Sku = firstPackageData["PackageSKU"].ToString(),
                Sku2 = firstPackageData["PackageSKU2"].ToString(),
                Brand = firstPackageData["PackageBrand"].ToString(),
                Description = firstPackageData["PackageDescription"].ToString(),
                Season = firstPackageData["PackageSeason"].ToString(),
                StyleCode = firstPackageData["PackageManSku"].ToString(),
                SupplierSKU = firstPackageData["SupplierSKU"].ToString(),
                SupplierSKU2 = firstPackageData["SupplierSKU2"].ToString(),
                OrderQuantity = (int)firstPackageData["OrderQty"],
                TotalBuyPrice = firstPackageItem ? (decimal?)firstPackageData["TotalBuyPrice"] ?? 0 : 0,
                isDuplicate = !firstPackageItem
            };

            packageData.Items = rows.AsEnumerable()
                                                //Again, we generate the individual items that the package comprises
                                                //We show a bit more information for a package component
                                                .Select(row => new VariantItem
                                                {
                                                    Sku = row["ProductSKU"].ToString(),
                                                    Sku2 = row["ProductSKU2"].ToString(),
                                                    ProdID = Convert.ToInt32(row["ProductProdID"].ToString()),
                                                    ManSku = row["ProductManSku"].ToString(),
                                                    Description = row["ProductDescription"].ToString(),
                                                    Brand = row["ProductBrand"].ToString(),
                                                    Season = row["ProductSeason"].ToString(),
                                                    Size = new ProductAttributeValue(row["ProductSize"].ToString(), null),
                                                    Colour = new ProductAttributeValue(row["ProductColour"].ToString(), null),
                                                    OrderQuantity = row["Units"] == DBNull.Value ? 0 : (int)row["Units"],
                                                    SupplierSKU = row["SupplierSKU"].ToString(),
                                                    SupplierSKU2 = row["SupplierSKU2"].ToString(),
                                                    isDuplicate = !firstPackageItem
                                                })
                                                .ToList();

            return packageData;
        }

        private List<VariantItem> createStandardProduct(List<DataRow> items)
        {
            //Finally, we have the standalone, non-package, non-matrix products. These go into the StandardItems collection
            //as variant products
            return items.AsEnumerable()
                            .Select(row => new VariantItem
                            {
                                Sku = row["ProductSKU"].ToString(),
                                Sku2 = row["ProductSKU2"].ToString(),
                                ProdID = ParseToInt(row["ProductProdID"]),
                                ManSku = row["ProductManSku"].ToString(),
                                Description = row["ProductDescription"]
                                                .ToString(),
                                Brand = row["ProductBrand"]
                                                .ToString(),
                                Season = row["ProductSeason"]
                                                .ToString(),
                                Size = new ProductAttributeValue(row["ProductSize"]
                                                                                .ToString(),
                                                                                null),
                                Colour = new ProductAttributeValue(row["ProductColour"]
                                                                                    .ToString(),
                                                                                null),
                                OrderQuantity = row["OrderQty"] == DBNull.Value ? 0 : (int)row["OrderQty"],
                                TotalBuyPrice = (decimal)row["TotalBuyPrice"],
                                SupplierSKU = row["SupplierSKU"]
                                                            .ToString(),
                                SupplierSKU2 = row["SupplierSKU2"]
                                                            .ToString()
                            })
                            .ToList();
        }

        private string ItemQueryText(PurchaseOrder.Format format)
        {
            string query = $@"
                WITH MatrixProducts AS
                (
                    SELECT  Manufacturer_Product_ID AS StyleCode
                    FROM    Products
                    WHERE   NULLIF(Manufacturer_Product_ID,'') IS NOT NULL";
            //If the format we're using doesn't have the Matrix option, we want to exclude matrix products
            //so we set an "always false" where clause
            if (!format.Has(PurchaseOrder.Format.Matrix))
            {
                query += @"
                            AND 1 = 0";
            }

            query += $@"
                    GROUP BY
                            Manufacturer_Product_ID
                    HAVING  COUNT(*) > 1
                ),
                PackageComponents AS
                (
                    SELECT  DISTINCT
                            component.Manufacturer_Product_ID AS StyleCode,
                            pack.Supplier_product_id AS PackageSKU,
                            pack.Supplier_product_id2 AS PackageSKU2,
                            pack.Product_ID AS PackageProductId,
                            component.Product_ID AS ComponentProductId,
                            pp.qty_in_package AS UnitsPerPackage,
                            ISNULL(component.ColourID, -1) AS ColourId,
                            ISNULL(c.Colour, '-') AS Colour,
                            ISNULL(component.SizeID, -1) AS SizeId,
                            ISNULL(s.Size, '-') AS Size
                    FROM    vwPOItem i
                            INNER JOIN Products_Package pp ON i.Product_ID = pp.primary_productid
                            INNER JOIN Products pack ON pp.primary_productid = pack.Product_ID
                            INNER JOIN Products component ON pp.secondary_productid = component.Product_ID
                            LEFT JOIN Colours c ON component.ColourID = c.ColourID
                            LEFT JOIN Sizes s ON component.SizeID = s.SizeID
                    WHERE   i.POID = @POID";
            //If we're not exploding packages, we again set an "always false" where clause
            if (!format.Has(PurchaseOrder.Format.ExplodedPackages))
            {
                query += @"
                            AND 1 = 0";
            }

            query += $@"
                ),
                MatrixStyles AS
                (
                    SELECT  pc.StyleCode
                    FROM    PackageComponents pc
                            INNER JOIN MatrixProducts mp ON pc.StyleCode = mp.StyleCode

                    UNION

                    SELECT  mp.StyleCode
                    FROM    vwPOItem i
                            INNER JOIN MatrixProducts mp ON i.Manufacturer_Product_ID = mp.StyleCode
                    WHERE   POID = @POID
                ),
                MasterProducts AS
                (
                    SELECT  StyleCode,
                            MIN(Product_ID) AS MasterProductId
                    FROM    MatrixStyles ms
                            INNER JOIN Products p ON ms.StyleCode = p.Manufacturer_Product_ID
                    GROUP BY
                            StyleCode
                ),
                MatrixPackages AS
                (
                    SELECT  DISTINCT
                            pc.PackageProductId
                    FROM    vwPOItem i
                            INNER JOIN PackageComponents pc ON i.Product_ID = pc.PackageProductId
                            INNER JOIN MasterProducts mp ON pc.StyleCode = mp.StyleCode
                    WHERE   i.POID = @POID
                )
                --Non-Package matrix products
                SELECT  CAST(1 AS BIT) AS IsMatrixProduct,
                        CAST(0 AS BIT) AS IsPackageProduct,
		                i.POItemID,
                        mp.StyleCode,
		                CAST(NULL AS VARCHAR(MAX)) AS PackageManSku,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageSKU,
		                CAST(NULL AS VARCHAR(MAX)) AS PackageSKU2,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageDescription,
		                CAST(NULL AS VARCHAR(MAX)) AS PackageProductId,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageBrand,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageSeason,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageSize,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageColour,
		                i.Supplier_product_id AS ProductSKU,
		                i.Supplier_product_id2 AS ProductSKU2,
		                i.Product_ID AS ProductProdID,
                        i.Manufacturer_Product_ID AS ProductManSku,
                        [master].Short_Description AS ProductDescription,
                        b.sBrand AS ProductBrand,
                        s.Season AS ProductSeason,
                        ISNULL(variant.SizeID, -1) AS ProductSizeId,
                        ISNULL(i.Size, '-') AS ProductSize,
                        sz.ListOrder AS ProductSizeListOrder,
                        ISNULL(variant.ColourID, -1) AS ProductColourId,
                        ISNULL(i.Colour, '-') AS ProductColour,
                        SUM(i.qtyOrdered) AS Units,
                        SUM(i.qtyOrdered) AS OrderQty,
                        SUM(i.qtyOrdered) AS TotalUnitsOrdered,
                        SUM(i.qtyOrdered * i.BuyPriceEx) AS TotalBuyPrice,
		                CAST(0 AS VARCHAR(MAX)) AS SupplierSKU,
                        CAST(0 AS VARCHAR(MAX)) AS SupplierSKU2,
		                CAST(NULL AS VARCHAR(MAX)) AS ChildProductID
                FROM    vwPOItem i
                        INNER JOIN Products variant ON i.Product_ID = variant.Product_ID
                        INNER JOIN MasterProducts mp ON i.Manufacturer_Product_ID = mp.StyleCode
                        INNER JOIN Products [master] ON mp.MasterProductId = [master].Product_ID
                        LEFT JOIN Brands b ON [master].Brand = b.iBrandID
                        LEFT JOIN Seasons s ON [master].SeasonID = s.SeasonID
                        LEFT JOIN Sizes sz ON variant.SizeID = sz.SizeID
                        LEFT JOIN PackageComponents pc ON i.Product_ID = pc.PackageProductId
                WHERE   i.POID = @POID
                        AND pc.PackageProductId IS NULL
                GROUP BY
                        mp.StyleCode,
                        [master].Short_Description,
                        b.sBrand,
                        s.Season,
                        ISNULL(variant.SizeID, -1),
                        ISNULL(i.Size, '-'),
                        sz.ListOrder,
                        ISNULL(variant.ColourID, -1),
                        ISNULL(i.Colour, '-'),
		                pc.PackageSKU2,
		                i.Product_ID,
		                i.Manufacturer_Product_ID,
		                i.Supplier_product_id,
		                i.Supplier_product_id2,
		                i.POItemID

                UNION ALL

                --Package matrix products
                SELECT  CAST(1 AS BIT) AS IsMatrixProduct,
                        CAST(1 AS BIT) AS IsPackageProduct,
		                i.POItemID,
                        pc.StyleCode,
		                i.Manufacturer_Product_ID AS PackageManSku,
                        pc.PackageSKU,
                        pc.PackageSKU2,
                        i.ShortDescription AS PackageDescription,
		                i.Product_ID AS PackageProductId,
                        i.Brand AS PackageBrand,
                        i.Season AS PackageSeason,
                        i.Size AS PackageSize,
                        i.Colour AS PackageColour,
                        [master].Supplier_product_id AS ProductSKU,
		                [master].Supplier_product_id2 AS ProductSKU2,
		                [master].Product_ID AS ProductProdID,
                        [master].Manufacturer_Product_ID AS ProductManSku,
                        [master].Short_Description AS ProductDescription,
                        b.sBrand AS ProductBrand,
                        s.Season AS ProductSeason,
                        pc.SizeId AS ProductSizeId,
                        pc.Size AS ProductSize,
                        sz.ListOrder AS ProductSizeListOrder,
                        pc.ColourId AS ProductColourId,
                        pc.Colour AS ProductColour,
                        pc.UnitsPerPackage AS Units,
                        SUM(i.qtyOrdered) AS OrderQty,
                        SUM(i.qtyOrdered * pc.UnitsPerPackage) AS TotalUnitsOrdered,
                        SUM(i.qtyOrdered * i.BuyPriceEx) AS TotalBuyPrice,
		                CASE WHEN ISNULL((SELECT SupplierPOTemplate.FieldName FROM SupplierPOTemplate
							                WHERE SupplierPOTemplate.SupplierId = sup.Supplier_ID 
								                AND SupplierPOTemplate.[Type]='SKUs' 
								                AND SupplierPOTemplate.FieldName='SupplierSKU'), '') = '' THEN 0
							                ELSE 1
			                END as SupplierSKU,
		                CASE WHEN ISNULL((SELECT SupplierPOTemplate.FieldName FROM SupplierPOTemplate
							                WHERE SupplierPOTemplate.SupplierId = sup.Supplier_ID 
								                AND SupplierPOTemplate.[Type]='SKUs' 
								                AND SupplierPOTemplate.FieldName='SupplierSKU2'), '') = '' THEN 0
							                ELSE 1
			                END as SupplierSKU2,
		                (SELECT CAST(tempPC.ComponentProductId AS nvarchar(50))  + ',' AS [text()] FROM PackageComponents tempPC 
			                WHERE i.Product_ID = tempPC.PackageProductId  
			                FOR XML PATH ('')) AS ChildProductID
                FROM    vwPOItem i
                        INNER JOIN PackageComponents pc ON i.Product_ID = pc.PackageProductId
                        INNER JOIN MasterProducts mp ON pc.StyleCode = mp.StyleCode
                        INNER JOIN Products [master] ON pc.ComponentProductId = [master].Product_ID
                        LEFT JOIN Brands b ON [master].Brand = b.iBrandID
                        LEFT JOIN Seasons s ON [master].SeasonID = s.SeasonID
                        LEFT JOIN Sizes sz ON pc.SizeID = sz.SizeID
		                INNER JOIN PO po ON i.POID = po.POID
		                INNER JOIN Suppliers sup ON po.Supplier_ID = sup.Supplier_Code
                WHERE   i.POID = @POID
                GROUP BY
                        pc.StyleCode,
                        pc.PackageSKU,
                        i.ShortDescription,
                        i.Brand,
                        i.Season,
                        i.Size,
                        i.Colour,
                        [master].Short_Description,
                        b.sBrand,
                        s.Season,
                        pc.SizeId,
                        pc.Size,
                        sz.ListOrder,
                        pc.ColourId,
                        pc.Colour,
                        pc.UnitsPerPackage,
		                pc.PackageSKU2,
		                sup.Supplier_ID,
		                i.Product_ID,
		                [master].Product_ID,
		                [master].Manufacturer_Product_ID,
		                [master].Supplier_product_id,
		                [master].Supplier_product_id2,
		                i.Manufacturer_Product_ID,
		                i.POItemID



                UNION ALL

                --Package non-matrix products
                SELECT  CAST(0 AS BIT) AS IsMatrixProduct,
                        CAST(1 AS BIT) AS IsPackageProduct,
		                i.POItemID,
                        pc.StyleCode,
		                i.Manufacturer_Product_ID AS PackageManSku,
		                pc.PackageSKU,
                        pc.PackageSKU2,
                        i.ShortDescription AS PackageDescription,
		                i.Product_ID AS PackageProductId,
                        i.Brand AS PackageBrand,
                        i.Season AS PackageSeason,
                        i.Size AS PackageSize,
                        i.Colour AS PackageColour,
		                p.Supplier_product_id as ProductSKU,
                        p.Supplier_product_id2 as ProductSKU2,
		                p.Product_ID AS ProductProdID,
                        p.Manufacturer_Product_ID AS ProductManSku,
                        p.Short_Description AS ProductDescription,
                        b.sBrand AS ProductBrand,
                        s.Season AS ProductSeason,
                        CAST(NULL AS INT) AS ProductSizeId,
                        sz.Size AS ProductSize,
                        CAST(NULL AS INT) AS ProductSizeListOrder,
                        CAST(NULL AS INT) AS ProductColourId,
                        c.Colour AS ProductColour,
                        pc.UnitsPerPackage AS Units,
                        SUM(i.qtyOrdered) AS OrderQty,
                        SUM(i.qtyOrdered * pc.UnitsPerPackage) AS TotalUnitsOrdered,
                        SUM(CASE WHEN matrix.PackageProductId = pc.PackageProductId
                                THEN NULL
                                ELSE i.qtyOrdered * i.BuyPriceEx
			                END) AS TotalBuyPrice,
		                CASE WHEN ISNULL((SELECT SupplierPOTemplate.FieldName FROM SupplierPOTemplate
							                WHERE SupplierPOTemplate.SupplierId = sup.Supplier_ID 
								                AND SupplierPOTemplate.[Type]='SKUs' 
								                AND SupplierPOTemplate.FieldName='SupplierSKU'), '') = '' THEN 0
							                ELSE 1
			                END as SupplierSKU,
		                CASE WHEN ISNULL((SELECT SupplierPOTemplate.FieldName FROM SupplierPOTemplate
						                WHERE SupplierPOTemplate.SupplierId = sup.Supplier_ID 
							                AND SupplierPOTemplate.[Type]='SKUs' 
							                AND SupplierPOTemplate.FieldName='SupplierSKU2'), '') = '' THEN 0
						                ELSE 1
			                END as SupplierSKU2,
		                (SELECT CAST(tempPC.ComponentProductId AS nvarchar(50)) + ',' AS [text()] FROM PackageComponents tempPC 
			                WHERE i.Product_ID = tempPC.PackageProductId  
			                FOR XML PATH ('')) AS ChildProductID
                FROM    vwPOItem i
                        INNER JOIN PackageComponents pc ON i.Product_ID = pc.PackageProductId
                        INNER JOIN Products p ON pc.ComponentProductId = p.Product_ID
                        LEFT JOIN Brands b ON p.Brand = b.iBrandID
                        LEFT JOIN Seasons s ON p.SeasonID = s.SeasonID
                        LEFT JOIN Sizes sz ON p.SizeId = sz.SizeID
                        LEFT JOIN Colours c ON p.ColourId = c.ColourId
                        LEFT JOIN MasterProducts mp ON pc.StyleCode = mp.StyleCode
                        LEFT JOIN MatrixPackages matrix ON pc.PackageProductId = matrix.PackageProductId
		                INNER JOIN PO po ON i.POID = po.POID
		                INNER JOIN Suppliers sup ON po.Supplier_ID = sup.Supplier_Code
                WHERE   i.poid = @poid
                        AND mp.StyleCode IS NULL
                GROUP BY
                        pc.PackageSKU,
                        i.ShortDescription,
                        i.Brand,
                        i.Season,
                        i.Size,
                        i.Colour,
                        p.Supplier_product_id,
		                p.Supplier_product_id2,
		                p.Product_ID,
		                p.Manufacturer_Product_ID,
                        p.Short_Description,
                        b.sBrand,
                        s.Season,
                        sz.Size,
                        c.Colour,
                        pc.UnitsPerPackage,
                        pc.PackageSKU2,
		                sup.Supplier_ID,
		                i.Manufacturer_Product_ID,
		                i.Product_ID,
		                pc.StyleCode,
		                i.POItemID

                UNION ALL

                --Non-package non-matrix products
                SELECT  CAST(0 AS BIT) AS IsMatrixProduct,
                        CAST(0 AS BIT) AS IsPackageProduct,
		                i.POItemID,
                        i.Manufacturer_Product_ID AS StyleCode,
		                CAST(NULL AS VARCHAR(MAX)) AS PackageManSKU,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageSKU,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageSKU2,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageDescription,
		                CAST(NULL AS VARCHAR(MAX)) AS PackageProductId,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageBrand,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageSeason,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageSize,
                        CAST(NULL AS VARCHAR(MAX)) AS PackageColour,
                        i.Supplier_product_id as ProductSKU,
                        i.Supplier_product_id2 as ProductSKU2,
		                i.Product_ID AS ProductProdID,
                        i.Manufacturer_Product_ID AS ProductManSku,
                        i.ShortDescription AS ProductDescription,
                        i.Brand AS ProductBrand,
                        i.Season AS ProductSeason,
                        CAST(NULL AS INT) AS ProductSizeId,
                        i.Size AS ProductSize,
                        CAST(NULL AS INT) AS ProductSizeListOrder,
                        CAST(NULL AS INT) AS ProductColourId,
                        i.Colour AS ProductColour,
                        CAST(NULL AS INT) AS Units,
                        SUM(i.qtyOrdered) AS OrderQty,
                        CAST(NULL AS INT) AS TotalUnitsOrdered,
                        SUM(i.qtyOrdered * i.BuyPriceEx) AS TotalBuyPrice,
		                CASE WHEN ISNULL((SELECT SupplierPOTemplate.FieldName FROM SupplierPOTemplate
							                WHERE SupplierPOTemplate.SupplierId = sup.Supplier_ID 
								                AND SupplierPOTemplate.[Type]='SKUs' 
								                AND SupplierPOTemplate.FieldName='SupplierSKU'), '') = '' THEN 0
							                ELSE 1
			                END as SupplierSKU,
		                CASE WHEN ISNULL((SELECT SupplierPOTemplate.FieldName FROM SupplierPOTemplate
						                WHERE SupplierPOTemplate.SupplierId = sup.Supplier_ID 
							                AND SupplierPOTemplate.[Type]='SKUs' 
							                AND SupplierPOTemplate.FieldName='SupplierSKU2'), '') = '' THEN 0
						                ELSE 1
			                END as SupplierSKU2,
		                CAST(NULL AS VARCHAR(MAX)) AS ChildProductID
                FROM    vwPOItem i
                        LEFT JOIN PackageComponents pc ON i.Product_ID = pc.PackageProductId
                        LEFT JOIN MasterProducts mp ON Manufacturer_Product_ID = mp.StyleCode
		                INNER JOIN PO po ON i.POID = po.POID
		                INNER JOIN Suppliers sup ON po.Supplier_ID = sup.Supplier_Code
                WHERE   i.poid = @poid
                        AND mp.StyleCode IS NULL
                        AND pc.PackageProductId IS NULL
                GROUP BY
                        i.Manufacturer_Product_ID,
                        i.Supplier_product_id,
		                i.Supplier_product_id2,
		                i.Product_ID,
                        i.ShortDescription,
                        i.Brand,
                        i.Season,
                        i.Size,
                        i.Colour,
		                pc.PackageSKU2,
		                sup.Supplier_ID,
		                i.POItemID";
            return query;
        }

        #endregion
        private struct MatrixProduct
        {
            public int ProductID;
            public string ProductSKU;
            public string ProductSKU2;
            public string Brand;
            public string Description;
            public string Season;
            public string StyleCode;
            public string SupplierSKU;
            public string SupplierSKU2;
            public bool isPackage;

            /// <summary>Indicates whether this instance and a specified object are equal.</summary>
            /// <param name="obj">The object to compare with the current instance. </param>
            /// <returns>
            /// <see langword="true" /> if <paramref name="obj" /> and this instance are the same type and represent the same value; otherwise, <see langword="false" />. </returns>
            public override bool Equals(object obj)
            {
                return obj != null && this.Equals((MatrixProduct)obj);
            }

            public bool Equals(MatrixProduct other)
            {
                return string.Equals(this.Brand,
                                     other.Brand) &&
                       string.Equals(this.Description,
                                     other.Description) &&
                       string.Equals(this.Season,
                                     other.Season) &&
                       string.Equals(this.StyleCode.ToLower(),
                                     other.StyleCode.ToLower());
            }

            /// <summary>Returns the hash code for this instance.</summary>
            /// <returns>A 32-bit signed integer that is the hash code for this instance.</returns>
            public override int GetHashCode()
            {
                unchecked
                {
                    int hashCode = (this.Brand != null ? this.Brand.GetHashCode() : 0);
                    hashCode = (hashCode * 397) ^ (this.Description != null ? this.Description.GetHashCode() : 0);
                    hashCode = (hashCode * 397) ^ (this.Season != null ? this.Season.GetHashCode() : 0);
                    hashCode = (hashCode * 397) ^ (this.StyleCode.ToLower() != null ? this.StyleCode.ToLower().GetHashCode() : 0);
                    return hashCode;
                }
            }
        }

        private int ParseToInt(object value)
        {
            int result = -1;
            Int32.TryParse(value?.ToString(), out result);

            return result;
        }
    }
}