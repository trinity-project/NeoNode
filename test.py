def md5_for_invoke_tx(tx_id, address_from, address_to, value, contract):
    import hashlib
    src = "{}{}{}{}{}".format(tx_id, address_from, address_to, value, contract).encode()
    m1 = hashlib.md5()
    m1.update(src)
    return m1.hexdigest()


x=md5_for_invoke_tx("0xc920b2192e74eda4ca6140510813aa40fef1767d00c152aa6f8027c24bdf14f2",
                  "AQcxz3gj42aZ74ymenykJuiMKBZqarFX6y",
                  "ATuT3d1cM4gtg6HezpFrgMppAV3wC5Pjd9",
                  "10000",
                  "0x0000000000000000000"
                  )
print(x)