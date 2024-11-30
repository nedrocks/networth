export interface Item {
  id: number;
  name: string;
  description: string;
  status: string;
}

export interface ItemList {
  items: Item[];
}