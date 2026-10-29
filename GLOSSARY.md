# eShop

A small online store where shoppers browse a catalog, fill a basket and place orders.

## Language

**Product**:
An item in the catalog that a shopper can view, favourite or add to their basket.
_Avoid_: Catalog item (in shopper-facing language), SKU

**Basket**:
The set of products a shopper intends to buy right now, with quantities.
_Avoid_: Cart

**Favourite**:
A product a signed-in shopper has saved to their account for later. It belongs to the account, survives sign-out, and is separate from the Basket: favouriting never adds to the basket, and adding to the basket never removes a favourite.
_Avoid_: Wishlist, saved item, bookmark, like

**Favourites page**:
The single page listing a signed-in shopper's Favourites, most recently saved first.
_Avoid_: Wishlist page, saved items
